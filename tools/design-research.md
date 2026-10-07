# Profile design research — 7 October 2026

The brief is to match the redesigned portfolio while avoiding repetitive, basic or overused profile templates. This is a qualitative selection of useful references, not an objective ranking of the “best” profiles.

| Reference | What makes it specific to its owner | Decision for this profile |
| --- | --- | --- |
| [Sindre Sorhus](https://github.com/sindresorhus/sindresorhus) | A deliberately nostalgic web aesthetic, with prominent links to his latest app and writing. | Keep a consistent personal visual language and direct product destinations. His retro GIF treatment does not match this portfolio. |
| [Cassidy Williams](https://github.com/cassidoo/cassidoo) | Personal voice and an easy-to-browse list of things she has made. | Use first-person ownership and real product links. Avoid a generic third-person biography. |
| [Simon Willison](https://github.com/simonw/simonw) | Recent releases, writing and learning notes make the profile useful on repeat visits. | Link directly to published releases and implementation evidence. An automated feed is unnecessary until there is a clear update source and cadence. |
| [Anthony Fu](https://github.com/antfu/antfu) | A very short navigation-oriented README that leaves the surrounding profile to carry context. | Keep the navigation compact, but retain product evidence because this profile serves internship evaluation too. |
| [Tim Burgan](https://github.com/timburgan/timburgan) | A community chess game makes interaction the central idea. | Include a small, optional route to Yousof’s own terminal and game. Do not copy the chess game or introduce issue-based interaction infrastructure. |
| [DenverCoder1](https://github.com/DenverCoder1/DenverCoder1) | A rich profile demonstrating the author’s README tooling and widgets. | Relevant as a reference for feature density, but counters, animated typing and dashboard-like stats would compete with the portfolio’s work-first presentation. |

The [Awesome GitHub Profile README collection](https://github.com/abhisheknaiidu/awesome-github-profile-readme) was used to compare broader categories: game mode, dynamic content, badges, typography, minimal profiles and image-led profiles. It is a discovery index, not evidence that a pattern is effective for every owner.

## Resulting design

- Exact portfolio identity: Hanken Grotesk, warm paper/charcoal, one natural portrait and current product screenshots.
- Three visible product compositions: a larger Bupples feature, a compact Adelante widget presentation, and a Photoshoot browser preview. One optional engineering disclosure contains deeper stories and the CodeAtlas and WayClub previews.
- Useful interaction: native disclosures reveal the Bupples settlement bug, Adelante widget synchronization, local regression evidence and database isolation. Each has a relevant case-study destination.
- A personal detour links to existing work: the portfolio terminal and the team-built Fallen Asteri game.
- Separate mobile compositions and light/dark images. Bespoke icon buttons retain the previous profile’s custom action treatment, with the new portfolio’s type, shape and colors. Native text retains ownership, status, tools and availability.
- No visitor counters, typing banners, trophy grids, contribution snakes, repeated contribution charts, animated wallpaper, logo walls or invented impact metrics.

## Platform evidence

[GitHub’s README quickstart](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/quickstart-for-writing-on-github) documents theme-aware `<picture>` elements and native `<details>` disclosures. The draft is passed through GitHub’s actual Markdown rendering endpoint before local browser inspection. SVGs use outlined fonts and embedded media, avoiding runtime font or image services.

[Simon Willison’s implementation article](https://simonwillison.net/2020/Jul/10/self-updating-profile-readme/) demonstrates how Actions can maintain useful sections. Automation was considered but is not required for this redesign; the content is deliberately curated and dated.
