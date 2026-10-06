// ===== 生き物アイコン（全ページ共通）=====
// ハンバーガーメニューと同じ線画（viewBox 24・線1.8・角丸）。
// 一部（シャチ・ジンベエザメ・アシカ・トドなど）は線と同じ色で塗りつぶし、白い模様は「くり抜き」で表している。
// 並び順がそのまま「生き物から探す」「集めた魚種印」「カードのタグ」「詳細ページ」の順になる。
// ※ app/main.py もこのファイルの JSON 部分を読んで詳細ページに使う。
//    window.CREATURES の [ ] の中身は「JSONとして正しい形」を保つこと（目印のコメントも消さない）。
window.CREATURES = /*CREATURES-JSON*/[
 {
  "key": "has_jellyfish",
  "name": "クラゲ",
  "svg": "<path d=\"M4.5 11.5a7.5 7.5 0 0 1 15 0z\"/><path d=\"M7.5 11.5c0 2 1 2.6 1 4.4s-1 2.4-1 4\"/><path d=\"M12 11.5c0 2.3 1 3 1 5s-1 2.6-1 4\"/><path d=\"M16.5 11.5c0 2-1 2.6-1 4.4s1 2.4 1 4\"/>"
 },
 {
  "key": "has_penguin",
  "name": "ペンギン",
  "svg": "<path d=\"M12 2.8c-2.9 0-4.4 2.4-4.4 5.6v5.2c0 3.8 1.9 6.9 4.4 6.9s4.4-3.1 4.4-6.9V8.4c0-3.2-1.5-5.6-4.4-5.6z\"/><path d=\"M12 9c-1.4 0-2.3 1.4-2.3 3.3v1.6c0 2.3 1 4 2.3 4s2.3-1.7 2.3-4v-1.6C14.3 10.4 13.4 9 12 9z\"/><path d=\"M7.6 10.5 5 14.8\"/><path d=\"M16.4 10.5 19 14.8\"/><path d=\"M11.2 6.6h1.6L12 7.7z\"/><circle cx=\"10.3\" cy=\"5.4\" r=\"0.6\" fill=\"currentColor\" stroke=\"none\"/><circle cx=\"13.7\" cy=\"5.4\" r=\"0.6\" fill=\"currentColor\" stroke=\"none\"/><path d=\"M9.6 20.6h-1.8\"/><path d=\"M14.4 20.6h1.8\"/>"
 },
 {
  "key": "has_dolphin",
  "name": "イルカ",
  "svg": "<path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M3.6 16.4C5.4 12 9.3 8.6 14.3 7.9c2.4-.3 4.3.3 5.6 1.5l2.9 1.1-3 1.1c-3.2 1.1-6.2 1.2-9 3.2-1.5 1.1-2.7 2.5-3.6 4.2l-1.6 3.1-.4-2.9L2.1 17.6z M17 9.9a0.6 0.6 0 1 0 1.2 0a0.6 0.6 0 1 0 -1.2 0z\"/><path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M11.3 8.9l1.5-3.6 2 3.1z\"/><path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M11.6 13.1l-.9 3.1 2.9-2.2z\"/>"
 },
 {
  "key": "has_orca",
  "name": "シャチ",
  "svg": "<path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M22.3 12.9c0-3.3-3.9-5.7-9-5.7-3.7 0-6.6 1.2-8.2 3.1L1.6 8.9l1.3 3.8-1.6 3.6 3.9-1.6c1 1 2.2 1.6 3.6 2 .6-1.4 2.3-2.6 4.8-2.9 2.9-.3 5.9 0 8.7-.9z M15.3 10.4a1.7 0.8 0 1 0 3.4 0a1.7 0.8 0 1 0 -3.4 0z\"/><path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M10.4 7.9 11.5 1.8l3.5 5.8z\"/><path d=\"M22.3 12.9c0 2.6-3.8 4.8-8.8 4.8-3.3 0-6.4-1.1-8.3-3\"/>"
 },
 {
  "key": "has_beluga",
  "name": "シロイルカ",
  "svg": "<path d=\"M4.6 14.6C6.3 11.3 9.2 9.6 12.6 9.5c.6-2.4 2.6-4.2 5.1-4.2 2.9 0 5 2.2 5 5 0 1.4-.6 2.4-1.7 2.9-.4.5-1.1.8-2 .7-2.3 1.4-4.7 2.6-8.2 2.6-2.6 0-4.4-.6-6.2-1.6\"/><path d=\"M6.5 15.1 3 17.9l.5-3.3-2.2-2.5 3.3 2\"/><path d=\"M12 14l-.5 2.6 2.2-1.4\"/><circle cx=\"18.3\" cy=\"10.2\" r=\"0.65\" fill=\"currentColor\" stroke=\"none\"/><path d=\"M19.4 12.7c.7.2 1.4.1 2-.3\"/>"
 },
 {
  "key": "has_shark",
  "name": "サメ",
  "svg": "<path d=\"M22 12.6c-2.4-2.3-6-3.5-10-3.3-2.9.1-5.4.9-7.4 2.2L2.2 7.2l.8 5.3-1.4 4.6 3.1-3.3c2 1.3 4.6 2 7.4 2 4.3 0 7.8-1.2 9.9-3.2z\"/><path d=\"M9.3 9.6l3.4-5.4.9 5.2\"/><path d=\"M11.2 14.4l1.4 3.4 1.3-3.2\"/><path d=\"M15.6 11.2v2.2\"/><path d=\"M16.8 11.1v2.3\"/><path d=\"M18 11.2v2.1\"/><circle cx=\"19.3\" cy=\"11.6\" r=\"0.6\" fill=\"currentColor\" stroke=\"none\"/>"
 },
 {
  "key": "has_sealion",
  "name": "アシカ",
  "svg": "<circle cx=\"18.6\" cy=\"3.4\" r=\"2\"/><path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M7.3 20.6c-.7-3.6.3-6.9 2.6-9.3 1.4-1.4 2.4-3.1 3-5.1.4-1.4 1.6-2.2 2.9-1.8l2.8 1.5-.2.8-2.4.5c-.6.2-.9.7-1 1.4-.4 3.4-.1 6.6 1.2 9.4.4.9.9 1.7 1.4 2.6z M14.700000000000001 6.9a0.6 0.6 0 1 0 1.2 0a0.6 0.6 0 1 0 -1.2 0z M10.6 15.2c.4-.3.9-.2 1.1.2l-1.9 4.6c-.2.4-.7.5-1 .3z\"/><path d=\"M3.5 20.6h17\"/>"
 },
 {
  "key": "has_seal",
  "name": "アザラシ",
  "svg": "<circle cx=\"12\" cy=\"12\" r=\"8.6\"/><circle cx=\"9\" cy=\"10.6\" r=\"1.1\" fill=\"currentColor\" stroke=\"none\"/><circle cx=\"15\" cy=\"10.6\" r=\"1.1\" fill=\"currentColor\" stroke=\"none\"/><path d=\"M11.1 13.3h1.8l-.9.9z\"/><path d=\"M12 14.2v.6c0 .8-.7 1.3-1.5 1.3\"/><path d=\"M12 14.8c0 .8.7 1.3 1.5 1.3\"/><path d=\"M8.6 14.6l-3 .5\"/><path d=\"M8.8 15.8l-2.6 1.3\"/><path d=\"M15.4 14.6l3 .5\"/><path d=\"M15.2 15.8l2.6 1.3\"/>"
 },
 {
  "key": "has_steller",
  "name": "トド",
  "svg": "<path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M2.6 19.4c.4-2.7 2.5-4.6 5.6-5.1 1.7-.3 2.9-1.3 3.8-2.8 1-1.8 1.4-3.8 2.8-5.1 1.3-1.2 3.2-1.3 4.6-.3l2.4 1.5-.2.7-2.2.6c-.6.2-.9.7-.9 1.4.1 3-.4 5.6-1.7 7.9-.4.7-.9 1.2-1.3 1.2z M16.799999999999997 7.6a0.6 0.6 0 1 0 1.2 0a0.6 0.6 0 1 0 -1.2 0z M12.4 11.3c1.4.8 3 1 4.6.7l-.2.8c-1.6.3-3.3 0-4.8-.8z\"/><path d=\"M1.6 19.6h20.8\"/>"
 },
 {
  "key": "has_walrus",
  "name": "セイウチ",
  "svg": "<path d=\"M4.2 11.5C4.2 6.9 7.7 3.5 12 3.5s7.8 3.4 7.8 8c0 1.5-.4 2.8-1.1 3.8\"/><path d=\"M5.3 15.3c-.7-1-1.1-2.3-1.1-3.8\"/><circle cx=\"9.3\" cy=\"8.6\" r=\"0.7\" fill=\"currentColor\" stroke=\"none\"/><circle cx=\"14.7\" cy=\"8.6\" r=\"0.7\" fill=\"currentColor\" stroke=\"none\"/><path d=\"M12 12.6c-.9-1.4-2.3-2-3.8-2-2 0-3.4 1.4-3.4 3.2s1.4 3 3.4 3c1.5 0 2.9-.8 3.8-2.2.9 1.4 2.3 2.2 3.8 2.2 2 0 3.4-1.2 3.4-3s-1.4-3.2-3.4-3.2c-1.5 0-2.9.6-3.8 2z\"/><path d=\"M10.3 16.4l-.6 5\"/><path d=\"M13.7 16.4l.6 5\"/>"
 },
 {
  "key": "has_whaleshark",
  "name": "ジンベエザメ",
  "svg": "<path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M22.7 11.8c0-1.7-2.6-3-9.3-3-3.4 0-6 .6-8 1.6L1.4 7.6l1 4.6-1 4.5 3.9-2.7c2 1 4.6 1.6 8.1 1.6 6.7 0 9.3-1.2 9.3-3.8z M7.450000000000001 11.6a0.85 0.85 0 1 0 1.7 0a0.85 0.85 0 1 0 -1.7 0z M10.1 10.6a0.8 0.8 0 1 0 1.6 0a0.8 0.8 0 1 0 -1.6 0z M10.55 13.4a0.85 0.85 0 1 0 1.7 0a0.85 0.85 0 1 0 -1.7 0z M13.35 11.6a0.85 0.85 0 1 0 1.7 0a0.85 0.85 0 1 0 -1.7 0z M16.15 10.5a0.75 0.75 0 1 0 1.5 0a0.75 0.75 0 1 0 -1.5 0z M16.45 13.3a0.75 0.75 0 1 0 1.5 0a0.75 0.75 0 1 0 -1.5 0z M22.7 12.4c-1 .4-2.4.6-4 .6v.8c1.7 0 3-.2 4-.6z\"/><path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M12.6 15.2l1.4 3 1.2-2.9z\"/>"
 },
 {
  "key": "has_ray",
  "name": "エイ",
  "svg": "<path d=\"M12 4.5c1.2 0 2.1 1 2.6 2.4 1.6 1.5 4.3 3.3 7 3.6-1.8 2-5 4.6-7.6 5.6-.8.3-1.4.4-2 .4s-1.2-.1-2-.4c-2.6-1-5.8-3.6-7.6-5.6 2.7-.3 5.4-2.1 7-3.6C9.9 5.5 10.8 4.5 12 4.5z\"/><path d=\"M12 16.5v5.5\"/><circle cx=\"10.6\" cy=\"8.2\" r=\"0.6\" fill=\"currentColor\" stroke=\"none\"/><circle cx=\"13.4\" cy=\"8.2\" r=\"0.6\" fill=\"currentColor\" stroke=\"none\"/>"
 },
 {
  "key": "has_sunfish",
  "name": "マンボウ",
  "svg": "<path d=\"M19.5 12c0 3.6-3 6.2-7 6.2-3.2 0-6-1.6-7.2-4.2-.3-.7-.3-3.3 0-4 1.2-2.6 4-4.2 7.2-4.2 4 0 7 2.6 7 6.2z\"/><path d=\"M11.2 6l-.8-4 3.4 4.2\"/><path d=\"M11.2 18l-.8 4 3.4-4.2\"/><path d=\"M5.4 10c-1 .4-2 1.1-2.9 2 .9.9 1.9 1.6 2.9 2\"/><path d=\"M15 12.6c.5.4 1.2.5 1.8.2\"/><circle cx=\"16.4\" cy=\"10.3\" r=\"0.6\" fill=\"currentColor\" stroke=\"none\"/>"
 },
 {
  "key": "has_seaotter",
  "name": "ラッコ",
  "svg": "<circle cx=\"5.8\" cy=\"10.4\" r=\"3.7\"/><circle cx=\"4.5\" cy=\"10\" r=\"0.6\" fill=\"currentColor\" stroke=\"none\"/><circle cx=\"7.1\" cy=\"10\" r=\"0.6\" fill=\"currentColor\" stroke=\"none\"/><path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M5.2 11.1h1.2l-.6.7z\"/><path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M9.3 10.9c1.9-.9 4.2-1.3 6.5-1.2 3.3.1 5.7 1.3 6.9 3.1-1.2 2.2-4.4 3.6-8.1 3.6-2.3 0-4.4-.4-6-1.3.6-1.3.8-2.6.7-4.2z M12.2 13.8a2.6 2.6 0 0 1 5.2 0z\"/><circle cx=\"12.3\" cy=\"13.6\" r=\"0.8\" fill=\"currentColor\" stroke=\"none\"/><circle cx=\"17.3\" cy=\"13.6\" r=\"0.8\" fill=\"currentColor\" stroke=\"none\"/><path d=\"M1.5 20c1.4 0 1.4-1 2.8-1s1.4 1 2.8 1 1.4-1 2.8-1 1.4 1 2.8 1 1.4-1 2.8-1 1.4 1 2.8 1 1.4-1 2.8-1\"/>"
 },
 {
  "key": "has_otter",
  "name": "カワウソ",
  "svg": "<path d=\"M12 5.4c4.8 0 8.4 2.8 8.4 6.8s-3.6 6.8-8.4 6.8-8.4-2.8-8.4-6.8 3.6-6.8 8.4-6.8z\"/><path d=\"M4.3 9.2a1.6 1.6 0 0 1 1.9-2.4\"/><path d=\"M19.7 9.2a1.6 1.6 0 0 0-1.9-2.4\"/><circle cx=\"8.7\" cy=\"11\" r=\"1\" fill=\"currentColor\" stroke=\"none\"/><circle cx=\"15.3\" cy=\"11\" r=\"1\" fill=\"currentColor\" stroke=\"none\"/><path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M10.9 12.9h2.2c0 .7-.5 1.2-1.1 1.2s-1.1-.5-1.1-1.2z\"/><path d=\"M10.7 15.3c.5.5 1.3.3 1.3-.7 0 1 .8 1.2 1.3.7\"/><circle cx=\"8.6\" cy=\"14.4\" r=\"0.4\" fill=\"currentColor\" stroke=\"none\"/><circle cx=\"7.5\" cy=\"13.9\" r=\"0.4\" fill=\"currentColor\" stroke=\"none\"/><circle cx=\"15.4\" cy=\"14.4\" r=\"0.4\" fill=\"currentColor\" stroke=\"none\"/><circle cx=\"16.5\" cy=\"13.9\" r=\"0.4\" fill=\"currentColor\" stroke=\"none\"/>"
 },
 {
  "key": "has_turtle",
  "name": "ウミガメ",
  "svg": "<path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M6.6 13.2a5.4 6.6 0 1 0 10.8 0a5.4 6.6 0 1 0 -10.8 0z M7.4 13.2a4.6 5.8 0 1 0 9.2 0a4.6 5.8 0 1 0 -9.2 0z\"/><path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M8.1 13.2a3.9 5.1 0 1 0 7.8 0a3.9 5.1 0 1 0 -7.8 0z M14.17 14.45L12 15.7L9.83 14.45L9.83 11.95L12 10.7L14.17 11.95z\"/><path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M13.56 14.1L12 15L10.44 14.1L10.44 12.3L12 11.4L13.56 12.3z\"/><path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M12 1.8c1.2 0 2 .9 2 2.1 0 1-.5 1.8-1.2 2.3v1H11.2v-1c-.7-.5-1.2-1.3-1.2-2.3 0-1.2.8-2.1 2-2.1z\"/><path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M7.3 9.2 3.3 6.3c-.6-.4-1.2.2-.9.8l2.5 4.6z\"/><path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M16.7 9.2l4-2.9c.6-.4 1.2.2.9.8l-2.5 4.6z\"/><path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M7.9 17.6 5 20.4c-.4.4 0 1 .5.9l3.6-1.2z\"/><path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M16.1 17.6l2.9 2.8c.4.4 0 1-.5.9l-3.6-1.2z\"/>"
 },
 {
  "key": "has_gardeneel",
  "name": "チンアナゴ",
  "svg": "<path d=\"M2.5 20.5h19\"/><path d=\"M8 20.5c0-3.2-2.4-4.2-2.4-7.6 0-2.6 1.4-4.4 3.2-4.4\"/><path d=\"M16 20.5c0-3.8 2.4-5 2.4-8.7 0-2.9-1.5-4.8-3.4-4.8\"/><circle cx=\"9\" cy=\"9.7\" r=\"0.6\" fill=\"currentColor\" stroke=\"none\"/><circle cx=\"14.9\" cy=\"8.2\" r=\"0.6\" fill=\"currentColor\" stroke=\"none\"/>"
 },
 {
  "key": "has_seahorse",
  "name": "タツノオトシゴ",
  "svg": "<path d=\"M14.5 4.2c-1.4-1.2-3.6-1-4.6.4L6.5 6.2l3.3.4c-.3 1.7.5 3 1.7 3.9-2.4 1.4-3.6 3.6-3.1 6.2.4 2.3 2.4 3.6 4.3 3.3 1.6-.3 2.4-1.9 1.6-3.1-.6-.8-1.8-.8-2.2.1\"/><path d=\"M14.5 4.2c1.1 1 1.4 2.6.7 4.2-.5 1.2-.3 2.4.6 3.3 1 1 1.3 2.6.6 4\"/><path d=\"M15.6 8.4l2.2.4-1.8 1.4\"/><circle cx=\"11.6\" cy=\"5\" r=\"0.6\" fill=\"currentColor\" stroke=\"none\"/>"
 },
 {
  "key": "has_clownfish",
  "name": "カクレクマノミ",
  "svg": "<path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M19.2 12c0 2.9-3.2 5.1-7.2 5.1-2.7 0-5-1-6.2-2.5L1.8 17V7l4 2.4C7 8 9.3 6.9 12 6.9c4 0 7.2 2.2 7.2 5.1z M6.75 6C7.85 9.5 7.85 14.5 6.75 18L8.25 18C9.35 14.5 9.35 9.5 8.25 6z M10.4 6C11.7 9.5 11.7 14.5 10.4 18L12 18C13.3 14.5 13.3 9.5 12 6z M14 6C15.3 9.5 15.3 14.5 14 18L15.6 18C16.9 14.5 16.9 9.5 15.6 6z M17.45 10.8a0.55 0.55 0 1 0 1.1 0a0.55 0.55 0 1 0 -1.1 0z\"/><path d=\"M19.2 12c0 2.9-3.2 5.1-7.2 5.1-2.7 0-5-1-6.2-2.5L1.8 17V7l4 2.4C7 8 9.3 6.9 12 6.9c4 0 7.2 2.2 7.2 5.1z\"/>"
 },
 {
  "key": "has_coral",
  "name": "サンゴ",
  "svg": "<path d=\"M12 21v-7\"/><path d=\"M12 14c0-2.4-1.6-3.2-3.2-4.2C7.6 9 7 8 7 6.4V4.5\"/><path d=\"M12 14c0-2.1 1.4-3 2.8-3.8 1.4-.8 2.2-1.9 2.2-3.6V5\"/><path d=\"M8.6 9.6 4.5 8.5V6\"/><path d=\"M15.2 10l4.3-.6V7\"/><path d=\"M12 16.5 9.2 15V12.5\"/><path d=\"M7 21h10\"/>"
 },
 {
  "key": "has_capybara",
  "name": "カピバラ",
  "svg": "<path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M2.5 13.6c0-3.1 2.6-5.4 6.4-5.4h4.6c.8-1.3 2-2 3.6-2h3.4c1.1 0 1.9.8 1.9 1.9v3.8c0 .9-.7 1.6-1.6 1.6h-3.6c-.6 1.6-1.8 2.8-3.4 3.4V20h-2l-.2-2.4H8.5V20h-2v-2.9c-2.4-.7-4-1.9-4-3.5z M17.15 8.6a0.75 0.75 0 1 0 1.5 0a0.75 0.75 0 1 0 -1.5 0z\"/><path d=\"M15.7 6.6l-.6-1.4\"/>"
 },
 {
  "key": "has_salamander",
  "name": "サンショウウオ",
  "svg": "<path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M22.6 12.9c0-1.5-1.6-2.6-4.1-2.7-1.6-.1-2.9.3-4.4.5-2.4.3-4.6-.1-6.9.1-2.6.2-4.8 1.2-6.2 2.6 1.6-.2 3.1-.1 4.6.4 1.9.6 4 .9 6.2.9h4.6c3.9 0 6.2-.4 6.2-1.8z M19.349999999999998 11.6a0.55 0.55 0 1 0 1.1 0a0.55 0.55 0 1 0 -1.1 0z M22.6 13.1c-.9.3-2.1.4-3.4.4v.6c1.4 0 2.6-.1 3.4-.4z\"/><path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M8.4 13.6l-1.1 2.3h2.8l.3-2.1z\"/><path fill=\"currentColor\" fill-rule=\"evenodd\" stroke=\"none\" d=\"M15.2 13.9l-.9 2.1h2.8l.2-2z\"/><path d=\"M1.5 17.2h21\"/>"
 },
 {
  "key": "has_deepsea",
  "name": "深海生物",
  "svg": "<path d=\"M20 13c0 3.4-3.4 5.6-7.6 5.6-3 0-5.6-1.2-6.8-3.2L3 17.6V8.4l2.6 2.2c1.2-2 3.8-3.2 6.8-3.2C16.6 7.4 20 9.6 20 13z\"/><path d=\"M15 7.6c.4-2.4 2.2-4 4.4-3.8\"/><circle cx=\"20.3\" cy=\"4.4\" r=\"1.2\"/><path d=\"M20 14.4l-3.6-.6 3.3-1.4\"/><path d=\"M17.3 13.9l.4 1M15.9 13.6l.3 1.2\"/><circle cx=\"15.6\" cy=\"10.6\" r=\"0.6\" fill=\"currentColor\" stroke=\"none\"/>"
 }
]/*END*/;

// 生き物アイコンの <svg> を返す（cls で大きさを変える）
window.creatureSvg = function (key, cls) {
  var c = null;
  for (var i = 0; i < window.CREATURES.length; i++) {
    if (window.CREATURES[i].key === key) { c = window.CREATURES[i]; break; }
  }
  if (!c) return "";
  return "<svg class=\"creature-icon" + (cls ? " " + cls : "") + "\" viewBox=\"0 0 24 24\" aria-hidden=\"true\">" + c.svg + "</svg>";
};
