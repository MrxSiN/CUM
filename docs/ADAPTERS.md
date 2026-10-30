# Language and graph admission

`adapters.bf` reads a single language identifier and returns zero only for 1 (BF).
All other identifiers return nonzero unsupported status. This executable denial
must stay in place until an actual adapter and its evidence exist.

Current BF protection is narrower than BF language admission: `transform.bf`
independently rejects any pointer move, and BBC must validate syntax/build output.
Do not infer that recognizing an extension or admitting a BF request means all
programs are transformable. Explicit selected file operands must be reviewed.

## Native XAX adapter requirements

The inspected XAX commit uses canonical binary semantic graphs, not authoritative
human-written textual syntax. Native Windows seed operations are `inspect`,
`verify`, `edit`, `resolve` and `build`. `edit` creates a candidate that still needs
verification; it does not itself publish a workspace atomically. Native seed
declines/rejections are not acceptance.

A future BF adapter must consume canonical schema/interface observations, retain
base-root/generation, define real semantic changes and emit supported expected-root
transaction carriers. Generic hashing/storage may be delegated; graph eligibility,
mutation choice and recovery policy remain BF-owned. It must preserve evolution,
dependency and workspace recovery data, verify candidate graphs and independently
rebuild. The current Git regular-file scope may capture canonical graph bytes but
does not prove development-ready workspace restoration.

No graph mutation is emitted in this draft. BF compilation through XAX is a
separate capability and must never be labeled native XAX project protection.

## Additional language requirements

Java/Kotlin support needs BF-authored parsing/eligibility and transformation
decisions, actual compiler checks, real project behavior, exact recovery and safe
ABI/reflection/JNI/resource/hook preservation. No extension-only adapter is
provided. C/C++/Rust/Python and virtualization remain unimplemented.
