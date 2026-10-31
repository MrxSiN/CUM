/* Generic standards-library CMS adapter. No project or source-transformation policy. */
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.io.*;
import java.security.*;
import java.security.cert.X509Certificate;
import org.bouncycastle.asn1.ASN1ObjectIdentifier;
import org.bouncycastle.asn1.pkcs.PrivateKeyInfo;
import org.bouncycastle.asn1.cms.*;
import org.bouncycastle.cert.X509CertificateHolder;
import org.bouncycastle.cert.jcajce.JcaX509CertificateConverter;
import org.bouncycastle.cms.*;
import org.bouncycastle.cms.jcajce.*;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.bouncycastle.openssl.PEMParser;
import org.bouncycastle.openssl.jcajce.JcaPEMKeyConverter;
import org.bouncycastle.operator.OutputAEADEncryptor;

public final class StandardCms {
    private static final ASN1ObjectIdentifier MLKEM1024 = new ASN1ObjectIdentifier("2.16.840.1.101.3.4.4.3");

    private static Object pem(String path) throws Exception {
        try (PEMParser reader = new PEMParser(Files.newBufferedReader(Path.of(path), StandardCharsets.US_ASCII))) {
            Object value = reader.readObject();
            if (value == null || reader.readObject() != null) throw new IOException("Expected one PEM object");
            return value;
        }
    }

    private static void publish(Path destination, byte[] data) throws Exception {
        Path parent = destination.toAbsolutePath().getParent();
        if (Files.exists(destination) || !Files.isDirectory(parent)) throw new IOException("Output must be new");
        Path pending = Files.createTempFile(parent, ".pending-cms-", ".tmp");
        try {
            Files.write(pending, data);
            Files.createLink(destination, pending);
        } finally {
            Files.deleteIfExists(pending);
        }
    }

    private static byte[] encrypt(String certificate, Path source) throws Exception {
        X509CertificateHolder holder = (X509CertificateHolder)pem(certificate);
        if (!holder.getSubjectPublicKeyInfo().getAlgorithm().getAlgorithm().equals(MLKEM1024))
            throw new GeneralSecurityException("ML-KEM-1024 recipient required");
        X509Certificate cert = new JcaX509CertificateConverter().setProvider("BC").getCertificate(holder);
        CMSAuthEnvelopedDataGenerator generator = new CMSAuthEnvelopedDataGenerator();
        generator.addRecipientInfoGenerator(new JceKEMRecipientInfoGenerator(cert, CMSAlgorithm.AES256_WRAP)
            .setProvider("BC").setKDF(CMSAlgorithm.SHA256_HKDF));
        return generator.generate(new CMSProcessableFile(source.toFile()),
            (OutputAEADEncryptor)new JceCMSContentEncryptorBuilder(CMSAlgorithm.AES256_GCM).setProvider("BC").build())
            .toASN1Structure().getEncoded("DER");
    }

    private static byte[] decrypt(String identity, Path source) throws Exception {
        PrivateKeyInfo info = (PrivateKeyInfo)pem(identity);
        if (!info.getPrivateKeyAlgorithm().getAlgorithm().equals(MLKEM1024))
            throw new GeneralSecurityException("ML-KEM-1024 identity required");
        PrivateKey key = new JcaPEMKeyConverter().setProvider("BC").getPrivateKey(info);
        CMSAuthEnvelopedData envelope = new CMSAuthEnvelopedData(Files.readAllBytes(source));
        if (!envelope.getEncryptionAlgOID().equals(CMSAlgorithm.AES256_GCM.getId()))
            throw new GeneralSecurityException("AES-256-GCM content required");
        AuthEnvelopedData structure = AuthEnvelopedData.getInstance(envelope.toASN1Structure().getContent());
        GCMParameters gcm = GCMParameters.getInstance(structure.getAuthEncryptedContentInfo().getContentEncryptionAlgorithm().getParameters());
        if (gcm.getNonce().length != 12 || gcm.getIcvLen() != 16)
            throw new GeneralSecurityException("Expected a 96-bit nonce and 128-bit tag");
        for (Object value : structure.getRecipientInfos()) {
            Object infoObject = RecipientInfo.getInstance(value).getInfo();
            if (!(infoObject instanceof OtherRecipientInfo)) throw new GeneralSecurityException("KEM recipients only");
            OtherRecipientInfo other = (OtherRecipientInfo)infoObject;
            if (!other.getType().equals(CMSObjectIdentifiers.id_ori_kem)) throw new GeneralSecurityException("Unknown recipient format");
            KEMRecipientInfo recipientInfo = KEMRecipientInfo.getInstance(other.getValue());
            if (!recipientInfo.getKem().getAlgorithm().equals(MLKEM1024) || recipientInfo.getKem().getParameters() != null
                || !recipientInfo.getKdf().equals(CMSAlgorithm.SHA256_HKDF) || recipientInfo.getKekLength() != 32
                || !recipientInfo.getWrap().getAlgorithm().equals(CMSAlgorithm.AES256_WRAP) || recipientInfo.getWrap().getParameters() != null)
                throw new GeneralSecurityException("Unsupported KEM suite");
        }
        for (RecipientInformation recipient : envelope.getRecipientInfos().getRecipients()) {
            if (!(recipient instanceof KEMRecipientInformation)) continue;
            try {
                return recipient.getContent(new JceKEMAuthEnvelopedRecipient(key).setProvider("BC").setMinimumTagSize(128));
            } catch (CMSException error) {
                // A wrong KEM identity must never publish unauthenticated plaintext.
            }
        }
        throw new GeneralSecurityException("No authenticated recipient");
    }

    public static void main(String[] args) {
        try {
            if (args.length != 4) throw new IllegalArgumentException("operation identity input output");
            Security.addProvider(new BouncyCastleProvider());
            Path source = Path.of(args[2]), destination = Path.of(args[3]);
            // shortcut: the library buffers content; validate streaming before admitting large archives.
            byte[] result;
            if (args[0].equals("encrypt")) result = encrypt(args[1], source);
            else if (args[0].equals("decrypt")) result = decrypt(args[1], source);
            else throw new IllegalArgumentException("Unsupported operation");
            publish(destination, result);
        } catch (Exception error) {
            System.err.println("CMS_OPERATION_FAILED:" + error.getClass().getSimpleName());
            System.exit(2);
        }
    }
}
