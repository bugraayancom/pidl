#!/bin/bash

echo "🎭 Persona in the Loop (PIDL) Kurulum Scripti"
echo "=============================================="
echo ""

# Python versiyonu kontrolü
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python versiyonu: $python_version"

# Virtual environment oluştur
echo ""
echo "📦 Virtual environment oluşturuluyor..."
python3 -m venv venv

# Virtual environment aktif et
echo "🔄 Virtual environment aktifleştiriliyor..."
source venv/bin/activate

# Gereksinimleri yükle
echo ""
echo "📥 Paketler yükleniyor..."
pip install --upgrade pip
pip install -r requirements.txt

# .env dosyası kontrolü
echo ""
if [ ! -f .env ]; then
    echo "⚠️  .env dosyası bulunamadı!"
    echo "📝 .env dosyası oluşturuluyor..."
    cat > .env << EOF
# OpenAI API Anahtarı
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Anahtarı (opsiyonel)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Model Ayarları
DEFAULT_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.7
MAX_TOKENS=2000
EOF
    echo "✓ .env dosyası oluşturuldu"
    echo "💡 Lütfen .env dosyasını düzenleyip API anahtarlarınızı ekleyin!"
else
    echo "✓ .env dosyası mevcut"
fi

echo ""
echo "=============================================="
echo "✅ Kurulum tamamlandı!"
echo ""
echo "🚀 Uygulamayı başlatmak için:"
echo "   source venv/bin/activate"
echo "   streamlit run app.py"
echo ""
echo "📖 Daha fazla bilgi için README.md dosyasına bakın"
echo "=============================================="

