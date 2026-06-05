#!/bin/bash
set -euo pipefail

# Only run in remote web sessions
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

SKILLS_DIR="$HOME/.claude/skills"
mkdir -p "$SKILLS_DIR"

install_skill() {
  local name="$1"
  local repo="$2"
  if [ ! -f "$SKILLS_DIR/$name/SKILL.md" ]; then
    echo "Installing skill: $name"
    git clone --depth=1 "$repo" "$SKILLS_DIR/$name" 2>/dev/null
  fi
}

install_skill_from_subdir() {
  local name="$1"
  local repo="$2"
  local subdir="$3"
  if [ ! -f "$SKILLS_DIR/$name/SKILL.md" ]; then
    echo "Installing skill: $name"
    local tmp
    tmp=$(mktemp -d)
    git clone --depth=1 --filter=blob:none --sparse "$repo" "$tmp" 2>/dev/null
    cd "$tmp" && git sparse-checkout set "$subdir" 2>/dev/null
    mkdir -p "$SKILLS_DIR/$name"
    cp -r "$tmp/$subdir/." "$SKILLS_DIR/$name/"
    rm -rf "$tmp"
  fi
}

# prompt-master
install_skill "prompt-master" "https://github.com/nidhinjs/prompt-master.git"

# humanizer (SKILL.md está em subpasta, precisa copiar para raiz)
if [ ! -f "$SKILLS_DIR/humanizer/SKILL.md" ]; then
  echo "Installing skill: humanizer"
  git clone --depth=1 "https://github.com/Aboudjem/humanizer-skill.git" "$SKILLS_DIR/humanizer" 2>/dev/null
  # Copia SKILL.md da subpasta para a raiz
  if [ -f "$SKILLS_DIR/humanizer/skills/humanizer/SKILL.md" ]; then
    cp "$SKILLS_DIR/humanizer/skills/humanizer/SKILL.md" "$SKILLS_DIR/humanizer/SKILL.md"
  fi
fi

# fact-checker
install_skill_from_subdir "fact-checker" "https://github.com/inbharatai/claude-skills.git" "skills/fact-checker"

# frontend-slides
install_skill "frontend-slides" "https://github.com/zarazhangrui/frontend-slides.git"

# find-skills
install_skill_from_subdir "find-skills" "https://github.com/vercel-labs/skills.git" "skills/find-skills"

echo "Skills prontas: $(ls "$SKILLS_DIR" | tr '\n' ' ')"
