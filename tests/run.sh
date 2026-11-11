#!/bin/sh
# 回归测试：分别用仓库里的 content.tex（blank）和自动生成的压力文档（stress）编译 main.tex。
# 用法：sh tests/run.sh        编译结果在 tests/build/<用例>/main.pdf
# 编译出错、日志中出现模板警告（Package kt Warning）或内容冲出页面（Overfull \vbox）时判为失败。
# 本机和 fonts/ 都没有宋体、黑体、楷体、Times New Roman 时，用 TeX Live 自带的 Fandol 和
# TeX Gyre Termes 顶替，只为让编译通过（例如在 CI 上），版面与正式字体会有出入。
# 设置 KT_TEST_SUBSTITUTE=1 可强制使用顶替字体。
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
build="$root/tests/build"
status=0

link_font() { # 目标文件名 顶替字体
  if [ -z "${KT_TEST_SUBSTITUTE:-}" ] && [ -e "$root/fonts/$1" ]; then
    ln -sf "$root/fonts/$1" "$dir/fonts/$1"
  else
    sub=$(kpsewhich "$2" || true)
    if [ -n "$sub" ]; then ln -sf "$sub" "$dir/fonts/$1"; fi
  fi
}

prepare() { # 用例名
  dir="$build/$1"
  mkdir -p "$dir/fonts"
  cp "$root/main.tex" "$root/.latexmkrc" "$dir/"
  ln -sf "$root/fonts/STXINGKA.ttf" "$dir/fonts/STXINGKA.ttf"
  link_font Simsun.ttc FandolSong-Regular.otf
  link_font SimHei.ttf FandolHei-Regular.otf
  link_font Kaiti.ttf FandolKai-Regular.otf
  link_font times.ttf texgyretermes-regular.otf
  link_font timesbd.ttf texgyretermes-bold.otf
  link_font timesi.ttf texgyretermes-italic.otf
  link_font timesbi.ttf texgyretermes-bolditalic.otf
}

compile() { # 用例名
  dir="$build/$1"
  if (cd "$dir" && latexmk -gg -interaction=nonstopmode -halt-on-error main.tex >build.out 2>&1); then
    pages=$(sed -n 's/^Output written on .*(\([0-9]*\) pages.*/\1/p' "$dir/main.log" | tail -1)
    if grep -E 'Package kt Warning|Overfull \\vbox' "$dir/main.log"; then
      echo "FAIL $1：日志中有上述警告"; status=1
    else
      echo "ok   $1：${pages} 页"
    fi
  else
    echo "FAIL $1：编译出错，见 $dir/main.log"; grep -A3 '^! ' "$dir/main.log" | head -20 || true
    status=1
  fi
}

prepare blank
cp "$root/content.tex" "$root/references.bib" "$build/blank/"
compile blank

prepare stress
python3 "$root/tests/gen_stress.py" "$root" "$build/stress"
compile stress

exit $status
