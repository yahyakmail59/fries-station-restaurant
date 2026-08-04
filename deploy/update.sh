#!/usr/bin/env bash
#
# تحديث فرايز ستيشن على PythonAnywhere.
#
# يُشغَّل من Bash Console على الخادم:
#     cd ~/fries-station-restaurant && bash deploy/update.sh
#
# الترتيب هنا مقصود: النسخة الاحتياطية أولًا لأنها مسار الرجوع الوحيد، ثم
# check قبل migrate لأن خطأ الإعدادات يجب أن يظهر قبل لمس قاعدة البيانات، ثم
# collectstatic أخيرًا لأنه الأثقل ولا معنى لتشغيله إن فشل ما قبله.
#
# set -e يوقف التنفيذ عند أول فشل، و-u يكشف المتغيرات غير المعرّفة، و
# pipefail يمنع أنبوبًا فاشلًا من الظهور ناجحًا.
set -euo pipefail

BRANCH="${BRANCH:-rebrand/fries-station}"
APP_DIR="${APP_DIR:-$HOME/fries-station-restaurant}"
BACKUP_DIR="${BACKUP_DIR:-$HOME/backups/fries-station}"
PY="$APP_DIR/.venv/bin/python"

# مرِّر --clear لحذف الملفات الثابتة القديمة قبل توليدها. يوفّر مساحة القرص
# لكنه يحذف قبل النسخ فتظهر 404 لثوانٍ — استخدمه في وقت هادئ فقط.
CLEAR=""
[ "${1:-}" = "--clear" ] && CLEAR="--clear"

step() { printf '\n\033[1;34m==> %s\033[0m\n' "$1"; }

cd "$APP_DIR"

step "فحص الحالة قبل البدء"
if [ -n "$(git status --porcelain)" ]; then
    echo "توجد تعديلات محلية على الخادم تمنع السحب بـ--ff-only:"
    git status --short
    echo
    echo "عالجها أولًا: git checkout -- <file>  أو  git stash"
    exit 1
fi
echo "شجرة العمل نظيفة."

step "نسخة احتياطية"
mkdir -p "$BACKUP_DIR"
# اسم زمني لكل نشر. الاسم الثابت كان يمحو نسخة النشر السابق في كل مرة،
# فتبقى نسخة واحدة فقط ولا يمكن الرجوع خطوتين.
STAMP="$(date +%Y%m%d-%H%M%S)"
if [ -f db.sqlite3 ]; then
    # .backup آمن أثناء عمل التطبيق، بخلاف نسخ الملف مباشرة.
    sqlite3 db.sqlite3 ".backup '$BACKUP_DIR/db-$STAMP.sqlite3'"
    echo "قاعدة البيانات -> db-$STAMP.sqlite3"
fi
git rev-parse HEAD > "$BACKUP_DIR/commit-$STAMP.txt"
echo "commit الحالي -> commit-$STAMP.txt  ($(git rev-parse --short HEAD))"

step "سحب $BRANCH من GitHub"
git pull --ff-only origin "$BRANCH"

step "فحص الإعدادات"
"$PY" manage.py check

step "فحص migrations ناقصة"
"$PY" manage.py makemigrations --check --dry-run

step "تطبيق migrations"
"$PY" manage.py migrate --noinput

step "توليد الملفات الثابتة ${CLEAR:+(مع --clear)}"
"$PY" manage.py collectstatic --noinput $CLEAR

step "إعادة تحميل التطبيق"
# لمس ملف WSGI يعيد تحميل التطبيق على PythonAnywhere دون فتح تبويب Web.
WSGI="$(ls /var/www/*_wsgi.py 2>/dev/null | head -1 || true)"
if [ -n "$WSGI" ]; then
    touch "$WSGI"
    echo "تم لمس $WSGI — التطبيق يُعاد تحميله."
else
    echo "لم أجد ملف WSGI. اضغط Reload يدويًا من تبويب Web."
fi

step "تم"
echo "الإصدار المنشور: $(git rev-parse --short HEAD) — $(git log -1 --pretty=%s)"
echo "للرجوع: راجع $BACKUP_DIR/commit-$STAMP.txt"
