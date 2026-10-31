"""Independent inspection of disposable RSA/GCM test envelopes; never production keys."""


def children(data):
    values = []
    while data:
        tag, length = data[0], data[1]
        header = 2
        if length & 128:
            count = length & 127
            assert 0 < count <= len(data)-2
            length = int.from_bytes(data[2:2+count], 'big'); header += count
        assert header+length <= len(data)
        values.append((tag, data[header:header+length]))
        data = data[header+length:]
    return values


def wrapped_keys_and_nonce(data):
    outer = children(data)
    assert len(outer) == 1 and outer[0][0] == 0x30
    info = children(outer[0][1])
    assert info[1][0] == 0xa0
    envelope = children(children(info[1][1])[0][1])
    recipients = next(body for tag, body in envelope if tag == 0x31)
    encrypted_keys = []
    for tag, body in children(recipients):
        assert tag == 0x30
        fields = children(body)
        assert fields[-1][0] == 4
        # These fixtures deliberately use standard RSA key transport.
        assert children(fields[-2][1])[0] == (6, bytes.fromhex('2a864886f70d010101'))
        encrypted_keys.append(fields[-1][1])
    encrypted_content = next(body for tag, body in envelope if tag == 0x30)
    algorithm = children(children(encrypted_content)[1][1])
    assert algorithm[0] == (6, bytes.fromhex('60864801650304012e'))
    parameters = children(algorithm[1][1])
    assert parameters[0][0] == 4 and len(parameters[0][1]) == 12
    return encrypted_keys, parameters[0][1]
