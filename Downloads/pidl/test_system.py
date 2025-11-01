#!/usr/bin/env python3
"""
PIDL Sistem Test Scripti
Sistemin tüm bileşenlerini test eder
"""

import os
import sys
from dotenv import load_dotenv

# .env yükle
load_dotenv()


def print_header(text):
    """Başlık yazdır"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def test_imports():
    """Import testleri"""
    print_header("📦 Import Testleri")
    
    try:
        print("Testing personas.py...", end=" ")
        from personas import get_all_personas, get_personas_by_category
        personas = get_all_personas()
        assert len(personas) == 10, "10 persona olmalı"
        print("✅")
        
        print("Testing code_generator.py...", end=" ")
        from code_generator import CodeGenerator
        print("✅")
        
        print("Testing evaluator.py...", end=" ")
        from evaluator import CodeEvaluator
        print("✅")
        
        print("\n✅ Tüm import'lar başarılı!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import hatası: {e}")
        return False


def test_personas():
    """Persona testleri"""
    print_header("👥 Persona Testleri")
    
    try:
        from personas import get_all_personas, get_personas_by_category
        
        personas = get_all_personas()
        print(f"✓ Toplam persona sayısı: {len(personas)}")
        
        education = get_personas_by_category("education")
        print(f"✓ Eğitim bilimcisi: {len(education)}")
        
        technology = get_personas_by_category("technology")
        print(f"✓ Teknoloji uzmanı: {len(technology)}")
        
        # Her persona'yı kontrol et
        print("\nPersona detayları:")
        for p in personas:
            print(f"  {p.avatar} {p.name} - {p.role}")
        
        assert len(personas) == 10, "10 persona olmalı"
        assert len(education) == 5, "5 eğitim bilimcisi olmalı"
        assert len(technology) == 5, "5 teknoloji uzmanı olmalı"
        
        print("\n✅ Tüm persona testleri başarılı!")
        return True
        
    except Exception as e:
        print(f"\n❌ Persona testi hatası: {e}")
        return False


def test_api_key():
    """API key testi"""
    print_header("🔑 API Key Testi")
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY bulunamadı!")
        print("💡 .env dosyasında OPENAI_API_KEY tanımlayın")
        return False
    
    if api_key == "your_openai_api_key_here":
        print("❌ API anahtarı varsayılan değerde!")
        print("💡 .env dosyasında gerçek API anahtarınızı girin")
        return False
    
    print(f"✓ API Key bulundu: {api_key[:10]}...{api_key[-4:]}")
    print("✅ API Key testi başarılı!")
    return True


def test_code_generator():
    """Code generator testi (API key gerekli)"""
    print_header("🤖 Code Generator Testi")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("⚠️  API anahtarı olmadan bu test atlanıyor")
        return None
    
    try:
        from code_generator import CodeGenerator
        from personas import get_all_personas
        
        print("✓ CodeGenerator başlatılıyor...")
        generator = CodeGenerator()
        
        print(f"✓ Model: {generator.model}")
        print(f"✓ Persona sayısı: {len(generator.personas)}")
        
        # Basit bir test (sadece 1 persona ile, maliyet azaltmak için)
        print("\n🧪 Basit kod üretim testi (1 persona)...")
        personas = get_all_personas()
        test_task = "İki sayının toplamını hesaplayan bir fonksiyon yaz"
        
        print(f"   Görev: {test_task}")
        print("   ⏳ Kod üretiliyor...")
        
        result = generator.generate_code_for_persona(personas[0], test_task)
        
        if result["success"]:
            print(f"   ✅ {result['persona_name']}: {result['tokens_used']} token")
            print("\n   Üretilen kod:")
            print("   " + "-" * 50)
            for line in result['code'].split('\n')[:10]:
                print(f"   {line}")
            if len(result['code'].split('\n')) > 10:
                print("   ...")
            print("   " + "-" * 50)
        else:
            print(f"   ❌ Hata: {result['error']}")
            return False
        
        print("\n✅ Code Generator testi başarılı!")
        return True
        
    except Exception as e:
        print(f"\n❌ Code Generator testi hatası: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_evaluator():
    """Evaluator testi"""
    print_header("📊 Evaluator Testi")
    
    try:
        from evaluator import CodeEvaluator
        
        test_code = """
def fibonacci(n):
    '''Fibonacci sayısını hesapla'''
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test
result = fibonacci(10)
print(f"Fibonacci(10) = {result}")
"""
        
        print("✓ CodeEvaluator başlatılıyor...")
        evaluator = CodeEvaluator()
        
        print("✓ Test kodu değerlendiriliyor...")
        result = evaluator.evaluate_code(test_code, "test_1", "Test Persona")
        
        print(f"\n📈 Sonuçlar:")
        print(f"   • Toplam Skor: {result['total_score']:.2f}/100")
        print(f"   • Güvenlik: {result['security_score']:.2f}/100")
        print(f"   • Kalite: {result['quality_score']:.2f}/100")
        print(f"   • Karmaşıklık: {result['complexity_score']:.2f}/100")
        print(f"   • Maintainability: {result['maintainability_index']:.2f}/100")
        
        print("\n✅ Evaluator testi başarılı!")
        return True
        
    except Exception as e:
        print(f"\n❌ Evaluator testi hatası: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependencies():
    """Bağımlılık testleri"""
    print_header("📦 Bağımlılık Testleri")
    
    required_packages = [
        "streamlit",
        "openai",
        "pandas",
        "plotly",
        "radon",
        "pylint",
        "bandit",
        "dotenv"
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            if package == "dotenv":
                __import__("dotenv")
            else:
                __import__(package)
            print(f"✓ {package:15s} kurulu")
        except ImportError:
            print(f"❌ {package:15s} KURULU DEĞİL!")
            all_ok = False
    
    if all_ok:
        print("\n✅ Tüm bağımlılıklar kurulu!")
    else:
        print("\n❌ Bazı paketler eksik. Lütfen 'pip install -r requirements.txt' çalıştırın")
    
    return all_ok


def main():
    """Ana test fonksiyonu"""
    print("""
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║   🎭 Persona in the Loop (PIDL)                 ║
    ║      Sistem Test Scripti                        ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    results = {
        "Dependencies": test_dependencies(),
        "Imports": test_imports(),
        "Personas": test_personas(),
        "API Key": test_api_key(),
        "Evaluator": test_evaluator(),
    }
    
    # Code generator testi (API key varsa)
    if results["API Key"]:
        print("\n⚠️  Code Generator testi API çağrısı yapacak (token kullanımı)")
        response = input("Devam etmek istiyor musunuz? (y/n): ")
        if response.lower() == 'y':
            results["Code Generator"] = test_code_generator()
        else:
            results["Code Generator"] = None
            print("⏭️  Code Generator testi atlandı")
    
    # Özet
    print_header("📊 Test Özeti")
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ BAŞARILI"
        elif result is False:
            status = "❌ BAŞARISIZ"
        else:
            status = "⏭️  ATLANDI"
        
        print(f"{test_name:20s}: {status}")
    
    # Genel sonuç
    print("\n" + "=" * 60)
    failed = sum(1 for r in results.values() if r is False)
    passed = sum(1 for r in results.values() if r is True)
    skipped = sum(1 for r in results.values() if r is None)
    
    if failed == 0:
        print("🎉 TÜM TESTLER BAŞARILI!")
        print("\n✅ Sistem hazır! Şimdi çalıştırabilirsiniz:")
        print("   streamlit run app.py")
    else:
        print(f"⚠️  {failed} test başarısız oldu")
        print(f"   Başarılı: {passed}, Başarısız: {failed}, Atlanan: {skipped}")
        print("\n💡 Lütfen hataları düzeltin ve tekrar deneyin")
    
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

