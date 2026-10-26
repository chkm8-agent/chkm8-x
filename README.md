# chkm8-x

Part of **chkm8**, r3lik's autonomous crypto research and trading agent, built on a stock [Hermes Agent](https://hermes-agent.nousresearch.com) install. Main repo: [chkm8-agent/chkm8](https://github.com/chkm8-agent/chkm8).

Art and scripts for the @Chkm8_agent X profile: avatar (pfp) and banner.

- `pfp/`: avatar compositions (`compose_*.py`, HTML templates) and the current/final renders
- `banner/`: banner templates and renders
- `build_tarot_set.py`, `tarot_grade.py`: tarot-style set builder and palette grading

Uploading the avatar/banner needs OAuth 1.0a and is done by `x_set_avatar.py` / `x_set_banner.py`
in `chkm8-trading` (private). Design iterations (`pfp/variants/`, raw renders) are gitignored.

## License

MIT, see [LICENSE](LICENSE).
