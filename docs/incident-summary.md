# Incident summary

The [FBI's October 31 notice](https://www.fbi.gov/investigate/cyber/alerts/2026/north-korea-responsible-for-6-billion-binance-attack)
attributes the October 29, 2026 theft of over $6 billion from Binance to North
Korea's TraderTraitor activity and publishes associated wallet addresses.

[Binance's preliminary report](https://www.binance.com/en/square/post/384314395829022)
describes a tampered Homebrew installer, a fake interview assignment with
install-time execution, pyenv replacement on macOS, lateral access through an
internal AI tool, and stolen deployment credentials reaching wallet signing.
It also describes multi-chain transfers and EIP-7702 delegation abuse involving
50 signed transactions. Existing authorizations complicated containment;
MPC wallets required additional revocation work. The report withholds some
technical details and remains preliminary.

This project separates published wallet indicators from behavioral hypotheses.
It does not supply unpublished malware hashes, command-and-control domains,
or infrastructure. See [source records](../iocs/SOURCES.md) for provenance and
verification limits. Synthetic tests in later phases will evaluate rule behavior,
not establish real-world detection efficacy.
