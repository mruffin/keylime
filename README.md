## Remote Attestation
**Remote Attestation** is designed to prove a property of a system to a third party, which in this case, is you. It can provide proof that the execution environment can be trusted before beginning to execute code or before proceeding to deliver any secret information. Remote attestation can provide different services, such as measured boot attestation and runtime integrity monitoring, using a hardware-based cryptographic root of trust, otherwise known as a Trusted Platform Module (TPM).

If you want to **continuously** make sure that things aren’t being altered in real-time you can use Linux kernel's Integrity Measurement Architecture (IMA) with runtime integrity monitoring. The tools in this repository can help you do that. These tools are designed to work with [Keylime](https://keylime.dev/), a highly scalable remote boot attestation and runtime integrity measurement solution.


## Tools Breakdown
In this repository, you will find various tools to help you generate runtime policies for runtime integrity monitoring with Keylime, parse through errors in the Keylime Verfier, and more. 
