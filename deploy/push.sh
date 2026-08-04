#!/usr/bin/env bash
#
# رفع فرايز ستيشن إلى GitHub من جهازك.
#
# يُشغَّل من Git Bash على ويندوز:
#     bash deploy/push.sh "رسالة التغيير"
#
# يفحص قبل الرفع بدل بعده: الاختبارات تكشف الكسر وأنت ما زلت قادرًا على
# التراجع، أما بعد الدفع فالإصلاح يحتاج commit جديدًا.
set -euo pipefail

BRANCH="${BRANCH:-rebrand/fries-station}"
MSG="${1:-}"

step() { printf '\n\033[1;34m==> %s\033[0m\n' "$1"; }

cd "$(dirname "$0")/.."

if [ -z "$(git status --porcelain)" ]; then
    echo "لا توجد تغييرات للرفع. شجرة العمل نظيفة."
    # قد تكون هناك commits محلية لم تُدفع بعد.
    if [ -n "$(git log "origin/$BRANCH..HEAD" --oneline 2>/dev/null)" ]; then
        step "توجد commits غير مدفوعة"
        git log "origin/$BRANCH..HEAD" --oneline
        git push origin "$BRANCH"
        echo "تم الدفع."
    fi
    exit 0
fi

if [ -z "$MSG" ]; then
    echo "مررِّر رسالة التغيير:"
    echo "    bash deploy/push.sh \"وصف ما غيّرته\""
    exit 1
fi

step "التغييرات التي سترتفع"
git status --short

step "الاختبارات"
# ملفات الخط والصور لا تكسر الاختبارات، لكن تعديل قالب أو نموذج قد يكسرها،
# والفحص هنا أرخص من اكتشاف الكسر على الخادم.
python manage.py test 2>&1 | tail -4

step "فحص migrations ناقصة"
python manage.py makemigrations --check --dry-run

step "الإيداع والدفع"
git add -A
git commit -m "$MSG"
git push origin "$BRANCH"

step "تم"
echo "$(git rev-parse --short HEAD) — $MSG"
echo
echo "الخطوة التالية على PythonAnywhere:"
echo "    cd ~/fries-station-restaurant && bash deploy/update.sh"
