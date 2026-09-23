# doraemius-episode-files

Run-it-yourself files for Doraemius videos: the scripts, inputs and test images each episode
used. One folder per episode, and each folder has its own README.

| Episode | Folder | What's in it |
|---|---|---|
| EP005: TypeSafe's Jev AI model, self-hosted | [`ep005-typesafe-jev/`](ep005-typesafe-jev) | three test inputs + a one-shot script against jeff, an MIT open reproduction of Jev's API |
| EP006: Qwen3-VL local OCR | [`ep006-qwen3-vl-ocr/`](ep006-qwen3-vl-ocr) | the OCR scorer, the description probe (three controls), and the test image |
| EP007: [Qwen3 Coder 30B wrote a Minecraft-style game](https://www.youtube.com/watch?v=5M1_bqp6Bo0) | its own repo: [doraemius-mimecraft-voxel-game](https://github.com/doraemius/doraemius-mimecraft-voxel-game) | the game, every iteration, every prompt |

Everything runs locally on your own hardware; nothing here calls a paid API.

License: [MIT](LICENSE) for the scripts in this repo. Third-party projects they install keep their own licences.
