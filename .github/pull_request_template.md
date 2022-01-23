<!--
For features and bug fixes, before opening a PR, please open an issue describing
the bug or feature the PR will address. You can skip this step if it's a typo fix.

Replace this comment with a description of the change. Describe how it
addresses the linked issue.
-->

<!--
Link to relevant issues or previous PRs, one per line. Use "fixes" to
automatically close an issue.
-->

fixes #<issue number>

<!--
If needed, ensure each step in the checklist below is complete. If only docs were changed, these aren't relevant and can be removed.
-->

Checklist:

- [ ] Add tests that demonstrate the correct behavior of the change. Tests should fail without the change.
- [ ] Add or update relevant docs, in the `docs` folder and in code docstring.
- [ ] Add an entry in `CHANGES.md` summarizing the change and linking to the issue.
- [ ] Add `*Version changed*` or `*Version added*` note in any relevant docs and docstring.
- [ ] Run `pytest` and `tox`, no tests failed.
