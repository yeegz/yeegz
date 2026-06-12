<!-- ════════════════════════════════════════════════════════════
     Yousof Selim · @yeegz — liquid-glass profile
     Setup (2 min):
       1. This file + the /assets folder go in the repo  yeegz/yeegz
       2. Add snake.yml at  .github/workflows/snake.yml
       3. Actions tab → "Generate snake animation" → Run workflow (once)
     Palette: #070B14 canvas · #0D1525 glass · #13B9FD sky · #02569B deep
     ════════════════════════════════════════════════════════════ -->

<img src="assets/header.svg" width="100%" alt="Yousof Selim — Full-Stack & Cross-Platform Developer · open to SWE / technical PM internships" />

<p align="center">
  <a href="https://linkedin.com/in/ysf-slm" target="_blank"><img src="https://img.shields.io/badge/LinkedIn-070B14?style=for-the-badge&logo=linkedin&logoColor=13B9FD" alt="LinkedIn" /></a>
  &nbsp;
  <a href="https://yeegz.github.io" target="_blank"><img src="https://img.shields.io/badge/Portfolio-070B14?style=for-the-badge&logo=googlechrome&logoColor=13B9FD" alt="Portfolio" /></a>
  &nbsp;
  <a href="mailto:yousofselim2@gmail.com"><img src="https://img.shields.io/badge/Email-070B14?style=for-the-badge&logo=gmail&logoColor=13B9FD" alt="Email" /></a>
</p>

<img src="assets/divider.svg" width="100%" alt="" />

### `about_me.dart`

```dart
class YousofSelim extends Developer {
  @override
  final String role = 'Full-Stack & Cross-Platform Mobile Developer';

  final Degree education = const Degree(
    'BSc (Hons) Software Engineering',
    at: 'Sunway University × Lancaster University',
    graduating: 2027,
  );

  final int shippingSince = 2023; // freelance — real clients, real deadlines
  final String sideQuest = 'Digital Marketing Exec @ Sunway Cybersecurity Club';

  @override
  List<String> get drivenBy => [
        'minimalist, modern UI/UX',
        'liquid-glass interfaces',
        'the gap between "it works" and "it feels right"',
      ];

  final List<String> aiPairProgrammers = ['Claude', 'Cursor', 'Copilot']; // not shy about it

  Future<Internship> get nextChapter =>
      apply(roles: ['Software Engineering', 'Technical PM']);
}
```

### `pubspec.yaml`

```yaml
name: yousof_selim
description: Cross-platform apps with full-stack plumbing and obsessive UI polish.

environment:
  sdk: ">=2023.2.0"          # shipping as a freelancer since Feb 2023

dependencies:
  # mobile & frontend
  flutter: ^everything
  dart: ^fluent
  react_native: ^when_asked
  tailwind_css: ^utility_first

  # backend & data
  node_js: ^services
  rest_apis: ^hand_designed
  supabase: ^realtime_sync
  postgresql: ^relational
  firebase: ^firestore

  # languages
  typescript: ^typed
  javascript: ^es2023
  python: ^scripts_and_tools

dev_dependencies:
  claude: ^pair_programmer    # ai-assisted, openly
  cursor: ^daily_driver
  github_copilot: ^tab_tab_tab
  figma: ^where_ui_starts
  git: ^non_negotiable
  xcode: ^simulators
  godot: ^weekend_game_dev    # see: Fallen Asteri
```

<img src="assets/divider.svg" width="100%" alt="" />

### `shipped/`

<sub>real products with live repo data — tap any card</sub>

<table align="center">
  <tr>
    <td align="center" width="50%">
      <a href="https://github.com/yeegz/Bupples">
        <img src="https://github-readme-stats.vercel.app/api/pin/?username=yeegz&repo=Bupples&bg_color=0D1525&title_color=13B9FD&icon_color=13B9FD&text_color=94A3B8&hide_border=true&border_radius=24" alt="Bupples" />
      </a><br/>
      <sub><b>💸 Bupples</b> — group expense-splitting · Flutter + Supabase/Firebase real-time sync · shipped to <b>iOS & Android</b></sub>
    </td>
    <td align="center" width="50%">
      <a href="https://github.com/yeegz/yeegz.github.io">
        <img src="https://github-readme-stats.vercel.app/api/pin/?username=yeegz&repo=yeegz.github.io&bg_color=0D1525&title_color=13B9FD&icon_color=13B9FD&text_color=94A3B8&hide_border=true&border_radius=24" alt="Portfolio" />
      </a><br/>
      <sub><b>🪟 Portfolio</b> — liquid-glass personal site · HTML/CSS/JS · <a href="https://yeegz.github.io"><b>live on GitHub Pages</b></a></sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <a href="https://github.com/yeegz/To-Do-List-Board">
        <img src="https://github-readme-stats.vercel.app/api/pin/?username=yeegz&repo=To-Do-List-Board&bg_color=0D1525&title_color=13B9FD&icon_color=13B9FD&text_color=94A3B8&hide_border=true&border_radius=24" alt="Task Board" />
      </a><br/>
      <sub><b>✅ Task Board</b> — ClickUp-style to-do app · drag-and-drop, category tags, priority sorting</sub>
    </td>
    <td align="center" width="50%">
      <a href="https://github.com/yeegz/Fallen-Asteri">
        <img src="https://github-readme-stats.vercel.app/api/pin/?username=yeegz&repo=Fallen-Asteri&bg_color=0D1525&title_color=13B9FD&icon_color=13B9FD&text_color=94A3B8&hide_border=true&border_radius=24" alt="Fallen Asteri" />
      </a><br/>
      <sub><b>⚔️ Fallen Asteri</b> — 2D platformer in Godot · movement, combat systems, scene transitions</sub>
    </td>
  </tr>
  <tr>
    <td align="center" colspan="2">
      <a href="https://github.com/HatemSamad/Tajweed">
        <img src="https://github-readme-stats.vercel.app/api/pin/?username=HatemSamad&repo=Tajweed&show_owner=true&bg_color=0D1525&title_color=13B9FD&icon_color=13B9FD&text_color=94A3B8&hide_border=true&border_radius=24" alt="Tajweed" />
      </a><br/>
      <sub><b>📖 Tajweed</b> — UI/UX redesign of a Quranic-recitation learning platform · navigation & information architecture</sub>
    </td>
  </tr>
</table>

<img src="assets/divider.svg" width="100%" alt="" />

### `analytics/`

<p align="center">
  <img height="170" src="https://github-readme-stats.vercel.app/api?username=yeegz&show_icons=true&include_all_commits=true&count_private=true&hide_border=true&bg_color=0D1525&title_color=13B9FD&icon_color=13B9FD&text_color=94A3B8&ring_color=13B9FD&border_radius=24" alt="GitHub stats" />
  <img height="170" src="https://github-readme-stats.vercel.app/api/top-langs/?username=yeegz&layout=compact&langs_count=8&hide_border=true&bg_color=0D1525&title_color=13B9FD&text_color=94A3B8&border_radius=24" alt="Top languages" />
</p>

<p align="center">
  <img src="https://streak-stats.demolab.com?user=yeegz&hide_border=true&border_radius=24&background=0D1525&stroke=1E293B&ring=13B9FD&fire=13B9FD&currStreakNum=F1F5F9&currStreakLabel=13B9FD&sideNums=F1F5F9&sideLabels=94A3B8&dates=64748B" alt="Contribution streak" />
</p>

<p align="center">
  <img width="100%" src="https://github-readme-activity-graph.vercel.app/graph?username=yeegz&hide_border=true&radius=24&bg_color=0D1525&color=94A3B8&title_color=13B9FD&line=13B9FD&point=F1F5F9&area=true&area_color=13B9FD" alt="Contribution activity" />
</p>

<!-- 🐍 contribution snake, recolored to the palette
     (appears after snake.yml has run once — see comment at top) -->

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/yeegz/yeegz/output/github-snake-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/yeegz/yeegz/output/github-snake.svg" />
    <img alt="Contribution snake animation" src="https://raw.githubusercontent.com/yeegz/yeegz/output/github-snake-dark.svg" />
  </picture>
</p>

<img src="assets/footer.svg" width="100%" alt="Let's build something — open to SWE & technical PM internships · yeegz.github.io" />
