#!/usr/bin/env python3
"""
Video Vault: 動画追加スクリプト
動画ファイルを暗号化 → manifest更新 → GitHubにpush → 視聴URLを発行 を1コマンドで完結。

Usage:
  python3 add-video.py <video-path> <video-id> <title> <password> [expires-yyyy-mm-dd]

Example:
  python3 add-video.py ~/Downloads/sample.mp4 vid002 "サンプル動画" hello123
  python3 add-video.py ~/Downloads/sample.mp4 vid003 "期限付き動画" secret 2026-12-31
"""

import sys
import os
import json
import datetime
import subprocess
from pathlib import Path


def main():
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit(1)

    video_path = sys.argv[1]
    video_id = sys.argv[2]
    title = sys.argv[3]
    password = sys.argv[4]
    expires = sys.argv[5] if len(sys.argv) > 5 else None

    # スクリプトのあるディレクトリで実行
    script_dir = Path(__file__).parent.resolve()
    os.chdir(script_dir)

    # ファイル確認
    video_p = Path(video_path).expanduser()
    if not video_p.exists():
        print(f"❌ 動画ファイルが見つかりません: {video_p}")
        sys.exit(1)

    # ID検証
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', video_id):
        print(f"❌ 動画IDは半角英数・ハイフン・アンダースコアのみ使用可能: {video_id}")
        sys.exit(1)

    # サイズチェック
    size_mb = video_p.stat().st_size / (1024 * 1024)
    print(f"📹 動画: {video_p.name} ({size_mb:.1f}MB)")

    if size_mb > 100:
        print(f"⚠️  100MB超え。GitHub単一ファイル制限に引っかかります。")
        print(f"  圧縮推奨コマンド:")
        print(f'  ffmpeg -i "{video_p}" -c:v libx264 -crf 28 -preset slow -c:a aac -b:a 128k -movflags +faststart 出力.mp4')
        ans = input("このまま続行する？(y/N): ").strip().lower()
        if ans != 'y':
            sys.exit(0)

    # 暗号化
    enc_path = f"videos/{video_id}.enc"
    print(f"🔐 暗号化中（PBKDF2 100k回 + AES-256-GCM）...")
    try:
        result = subprocess.run(
            ["node", "encrypt.js", str(video_p), enc_path, password],
            capture_output=True, text=True, check=True
        )
        enc_info = json.loads(result.stdout)
        print(f"   ✓ 暗号化完了 → {enc_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ 暗号化失敗: {e.stderr}")
        sys.exit(1)

    # manifest.json 更新
    print("📝 manifest.json 更新...")
    manifest_p = Path("manifest.json")
    if manifest_p.exists():
        with manifest_p.open("r", encoding="utf-8") as f:
            manifest = json.load(f)
    else:
        manifest = {"videos": []}

    entry = {
        "id": video_id,
        "title": title,
        "file": enc_path,
        "salt": enc_info["salt"],
        "iv": enc_info["iv"],
        "contentType": "video/mp4",
        "expiresAt": expires,
        "createdAt": datetime.date.today().isoformat()
    }

    existing_idx = next(
        (i for i, v in enumerate(manifest["videos"]) if v["id"] == video_id),
        None
    )

    if existing_idx is not None:
        manifest["videos"][existing_idx] = entry
        action_msg = f"既存動画ID '{video_id}' を更新"
    else:
        manifest["videos"].append(entry)
        action_msg = f"新規動画ID '{video_id}' を追加"

    with manifest_p.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f"   ✓ {action_msg}")

    # git push
    print("📤 GitHubにpush...")
    try:
        subprocess.run(["git", "add", enc_path, "manifest.json"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"Add/update video: {title} ({video_id})"],
            check=True, capture_output=True
        )
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True)
        print("   ✓ push完了")
    except subprocess.CalledProcessError as e:
        print(f"❌ git操作失敗: {e}")
        if e.stderr:
            print(e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr)
        sys.exit(1)

    # 視聴URL生成
    remote = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True, text=True
    ).stdout.strip()

    if remote.startswith("git@github.com:"):
        user_repo = remote.replace("git@github.com:", "").replace(".git", "")
    elif remote.startswith("https://github.com/"):
        user_repo = remote.replace("https://github.com/", "").replace(".git", "")
    else:
        user_repo = remote

    parts = user_repo.split("/")
    if len(parts) >= 2:
        user, repo = parts[0], parts[1]
        url = f"https://{user.lower()}.github.io/{repo}/?id={video_id}"
    else:
        url = "（リモートURLからGitHub Pagesドメインを推測できませんでした）"

    print("")
    print("=" * 60)
    print("✅ 完了！（GitHub Pagesのビルドに1〜3分かかります）")
    print("=" * 60)
    print(f"🎬 タイトル  : {title}")
    print(f"🔑 パスワード: {password}")
    if expires:
        print(f"📅 有効期限  : {expires}")
    print(f"🔗 視聴URL   : {url}")
    print("")
    print("📋 スプシに貼る用:")
    print(f"   {title}\\t{url}\\t{password}")


if __name__ == "__main__":
    main()
