"""
Kod Üretim Motoru - LLM entegrasyonu ile persona'lar için kod üretimi
"""

import os
import asyncio
from typing import Dict, List, Optional
from dotenv import load_dotenv
import openai

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from personas import Persona, get_all_personas

# .env dosyasını yükle
load_dotenv()


class CodeGenerator:
    """Kod üretim sınıfı - OpenAI ve Anthropic desteği"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini",
                 provider: str = "openai", anthropic_key: Optional[str] = None):
        """
        CodeGenerator başlat

        Args:
            api_key: OpenAI API anahtarı (None ise env'den alınır)
            model: Kullanılacak model
            provider: "openai" veya "anthropic"
            anthropic_key: Anthropic API anahtarı (None ise env'den alınır)
        """
        self.provider = provider.lower()
        self.model = model
        self.personas = get_all_personas()

        # OpenAI client
        if self.provider == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OpenAI API anahtarı bulunamadı! .env dosyasını kontrol edin.")
            self.client = openai.OpenAI(api_key=self.api_key)
            self.anthropic_client = None

        # Anthropic client
        elif self.provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ValueError("Anthropic paketi yüklü değil! pip install anthropic")
            self.api_key = anthropic_key or os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("Anthropic API anahtarı bulunamadı! .env dosyasını kontrol edin.")
            self.anthropic_client = anthropic.Anthropic(api_key=self.api_key)
            self.client = None

        else:
            raise ValueError(f"Geçersiz provider: {provider}. 'openai' veya 'anthropic' olmalı.")
    
    def _create_persona_specific_prompt(self, persona: Persona, task: str) -> str:
        """
        Persona'nın kendi bakış açısıyla prompt oluşturur
        Her persona gerçek hayatta nasıl prompt yazarsa öyle yazar
        
        Args:
            persona: Persona objesi
            task: Kullanıcının verdiği basit görev
            
        Returns:
            Persona'nın kendi yazdığı prompt
        """
        # Persona kategorisine ve ID'sine göre özel prompt yazma stili
        
        if persona.id == "edu_1":  # Dr. Ayşe Öğretmen - Pedagog (Yazılım eğitimi yok)
            return f"""'{task}' için kod yaz.

SEN KİMSİN: Eğitim profesörüsün, yazılım geliştirme eğitimin yok.
Blockchain'i teorik biliyorsun ama Solidity/programlama konusunda acemisin.

YAKLAŞIMIN:
- Pedagojik düşünceyle yaklaş (hangi veriler gerekli, kim ne görmeli)
- Çok basit ve anlaşılır kod yazmaya çalış
- Bol yorum ekle (kendine de hatırlat)
- Karmaşık syntax bilmiyorsun, basit tut
- Best practice'leri tam bilmiyorsun
- ChatGPT'ye sorar gibi yaklaş

Elinden geldiğince çalışan bir kod yaz. Pedagojik açıdan doğru ama teknik olarak basit/eksik olabilir."""
        
        elif persona.id == "edu_2":  # Prof. Mehmet - Pedagog (Yazılım eğitimi yok)
            return f"""'{task}' için kod yaz.

SEN KİMSİN: Eğitim bilimleri profesörüsün, yazılım developer'ı değilsin.
Online kurslardan Python/Solidity öğreniyorsun.

YAKLAŞIMIN:
- Her adımı ayrı ayrı fonksiyonlara böl (anlaşılır olsun)
- Her fonksiyonda ne yaptığını açıkla
- Basit syntax kullan (ileri seviye bilmiyorsun)
- step1, step2 gibi isimler kullan
- Karmaşık pattern'leri bilmiyorsun

Adım adım, basit kod yaz. Teknik olarak eksik olabilir ama pedagojik açıdan düşünülmüş."""
        
        elif persona.id == "edu_3":  # Dr. Zeynep - Araştırmacı (Yazılım bilgisi sınırlı)
            return f"""'{task}' için kod yaz.

SEN KİMSİN: Psikoloji ve eğitim araştırmacısısın. R/SPSS biliyorsun ama Solidity/Python konusunda acemisin.

YAKLAŞIMIN:
- Problemi önce analiz et (araştırmacı mantığıyla)
- Farklı yaklaşımları düşün
- Ama kod yazarken basit kal (teknik bilgin sınırlı)
- Yorumlarda alternatiflerden bahset ama implementasyon basit
- Akademik düşünce var, teknik uygulama zayıf

Düşünceli ama teknik olarak basit kod yaz."""
        
        elif persona.id == "edu_4":  # Doç. Ali - Eğitim Koordinatörü (Non-technical)
            return f"""'{task}' için kod yaz.

SEN KİMSİN: Eğitim yöneticisisin, developer değilsin.
LMS kullanıyorsun ama kod yazmada çok acemisin.

YAKLAŞIMIN:
- Modüler düşün (eğitim yönetiminden biliyorsun)
- Basit fonksiyonlar yaz
- Her modülü açıkla ama teknik detay bilgisi yok
- Takım çalışması mantığıyla yaklaş
- Ama syntax ve best practice bilgin zayıf

Modüler düşünülmüş ama teknik olarak basit kod yaz."""
        
        elif persona.id == "edu_5":  # Dr. Fatma - EdTech (No-code background)
            return f"""'{task}' için kod yaz.

SEN KİMSİN: EdTech uzmanısın, no-code araçlar kullanıyorsun.
Gerçek kod yazmada yeni başlangıçsın.

YAKLAŞIMIN:
- Farklı kullanıcı seviyeleri düşün (eğitimden biliyorsun)
- Parametreler kullanmayı bil (config dosyası gibi)
- Ama teknik implementation çok basit
- if-else ile farklı modlar yapmaya çalış
- Advanced syntax bilmiyorsun

Adaptif düşünce var, teknik kod basit."""
        
        elif persona.id == "tech_1":  # Ahmet - Blockchain Developer (Pedagoji bilmiyor)
            return f"""'{task}' için production-ready smart contract yaz.

SEN KİMSİN: Professional blockchain developer'sın. Pedagoji/eğitim bilgin YOK.
Sadece teknik gereksinimlerle ilgilenirsin, eğitim teorileri umurunda değil.

YAKLAŞIMIN:
- Clean code, SOLID, best practices (teknik olarak mükemmel)
- NatSpec dokümantasyon, interface'ler
- Gas efficiency düşün (ama pedagoji düşünme)
- Kullanıcı kim olacak umurunda değil, kod çalışsın yeter
- Öğrenme, erişebilirlik, pedagoji kavramları bilmiyorsun

Teknik olarak mükemmel ama pedagojik düşünce YOK."""
        
        elif persona.id == "tech_2":  # Can - Blockchain DevOps (Pedagoji bilmiyor)
            return f"""'{task}' için gas-optimized smart contract yaz.

SEN KİMSİN: Blockchain DevOps'sın. Gas ve performans her şey. Pedagoji/eğitim bilgin YOK.

YAKLAŞIMIN:
- Minimum gas consumption (her wei sayar)
- Storage optimization, packed variables
- Scalable contract architecture
- Kullanıcı deneyimi umurunda değil, performans önemli
- Eğitim teorileri, öğrenme, erişebilirlik bilmiyorsun

Teknik olarak ultra-optimized ama pedagojik düşünce sıfır."""
        
        elif persona.id == "tech_3":  # Elif Security Expert
            # Solidity mı Python mi kontrol et
            if "solidity" in task.lower() or "smart contract" in task.lower():
                return f"""'{task}' için güvenlik-first smart contract yaz.

SEN KİMSİN: Smart contract auditor'sın. Güvenlik her şey. Pedagoji/eğitim bilgin YOK.

YAKLAŞIMIN:
- Reentrancy guard, SafeMath, access control (security first)
- Her satırda zafiyet kontrol et
- OpenZeppelin kullan, audited kütüphaneler
- Kullanıcı deneyimi, öğrenme umurunda değil - güvenlik önemli
- Pedagojik erişebilirlik, öğrenci motivasyonu bilmiyorsun

Teknik olarak ultra-secure ama eğitimsel düşünce sıfır."""
            else:
                return f"""'{task}' için güvenlik odaklı Python/Web3 kod yaz.
Her input'u validate et. Private key'leri asla hardcode etme.
Try-except ile hata yönetimi güvenli olsun.
Integer overflow, DOS attack gibi risklere dikkat et. Defensive programming."""
        
        elif persona.id == "tech_4":  # Deniz - DApp Architect (Pedagoji bilmiyor)
            return f"""'{task}' için full-stack DApp mimarisi yaz.

SEN KİMSİN: DApp architect'sin. Mimari her şey. Pedagoji/eğitim teorileri bilmiyorsun.

YAKLAŞIMIN:
- Layered architecture (smart contract + backend + frontend)
- Proxy patterns, upgradability
- Multi-chain compatibility
- Enterprise patterns, abstraction
- Kullanıcı öğrenme süreci umurunda değil, mimari doğru olsun
- Pedagojik erişebilirlik, öğrenci ihtiyaçları bilmiyorsun

Teknik olarak enterprise-grade ama eğitimsel perspektif sıfır."""
        
        elif persona.id == "tech_5":  # Burak AI Specialist
            # Solidity için gas optimization odaklı
            if "solidity" in task.lower() or "smart contract" in task.lower() or "gas" in task.lower():
                return f"""'{task}' için ULTRA GAS-OPTIMIZED Solidity kod yaz.

SEN KİMSİN: Gas optimization specialist'sin. Her wei önemli. Pedagoji/eğitim kavramları bilmiyorsun.

YAKLAŞIMIN:
- Minimum gas! Storage→Memory→Calldata, packed storage, unchecked
- Assembly/Yul kullanabilirsin (max optimization)
- EVM opcode seviyesinde düşün
- Kullanıcı öğrenme, UX umurunda değil - gas maliyeti önemli
- Öğrenci, öğretmen, pedagoji kavramları bilmiyorsun
- Sadece: "Bu ne kadar gas yer?" diye düşün

Teknik olarak ultra-optimized, her wei sayar. Eğitimsel düşünce sıfır."""
            else:
                return f"""'{task}' için algoritmik olarak optimal Python kod lazım.
En verimli algoritma ve veri yapısını seç. Big-O analizi yap.
Dynamic programming, memoization gibi teknikleri kullan gerekirse.
Matematiksel olarak elegant olsun. Time/space trade-off'ları düşün.
List comprehension ve generator kullan. Kod kısa ama güçlü olsun."""
        
        else:
            # Default (olmaması gereken durum)
            return f"""'{task}' için kendi uzmanlığıma göre kod yaz."""
    
    def generate_code_for_persona(self, persona: Persona, task: str) -> Dict:
        """
        Tek bir persona için kod üret
        
        Args:
            persona: Persona objesi
            task: Kod yazılacak görev
            
        Returns:
            Sonuç dictionary'si (persona_id, code, metadata)
        """
        try:
            # Persona'nın kendi perspektifinden prompt oluştur
            # Bu, persona'nın gerçek dünyada nasıl prompt yazacağını simüle eder
            persona_prompt = self._create_persona_specific_prompt(persona, task)
            
            # Tam prompt hazırla
            user_prompt = f"""
Görev: {task}

Senin perspektifin ve uzmanlığınla bu görevi şöyle yorumluyorsun:
"{persona_prompt}"

Bu yoruma göre Python kodu yaz. Kodun:
- Çalışabilir ve test edilebilir olmalı
- Kendi uzmanlık alanına ve felsefene göre yaklaşmalısın
- Gerekli import'ları ekle
- Fonksiyonel ve eksiksiz olmalı

Sadece Python kodunu yaz, başka açıklama ekleme. Kod blokları olmadan direkt kodu yaz.
"""
            
            # Provider'a göre API çağrısı
            if self.provider == "openai":
                # OpenAI API çağrısı
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": persona.system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                generated_code = response.choices[0].message.content.strip()
                tokens_used = response.usage.total_tokens

            elif self.provider == "anthropic":
                # Anthropic API çağrısı
                response = self.anthropic_client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    system=persona.system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                generated_code = response.content[0].text.strip()
                tokens_used = response.usage.input_tokens + response.usage.output_tokens

            # Kod bloklarını temizle
            if generated_code.startswith("```python"):
                generated_code = generated_code[9:]
            elif generated_code.startswith("```"):
                generated_code = generated_code[3:]
            if generated_code.endswith("```"):
                generated_code = generated_code[:-3]

            generated_code = generated_code.strip()

            return {
                "persona_id": persona.id,
                "persona_name": persona.name,
                "persona_role": persona.role,
                "category": persona.category,
                "avatar": persona.avatar,
                "code": generated_code,
                "persona_prompt": persona_prompt,
                "success": True,
                "error": None,
                "tokens_used": tokens_used,
                "provider": self.provider,
                "model": self.model
            }
            
        except Exception as e:
            return {
                "persona_id": persona.id,
                "persona_name": persona.name,
                "persona_role": persona.role,
                "category": persona.category,
                "avatar": persona.avatar,
                "code": f"# Hata oluştu: {str(e)}",
                "persona_prompt": persona_prompt if 'persona_prompt' in locals() else "N/A",
                "success": False,
                "error": str(e),
                "tokens_used": 0
            }
    
    async def generate_code_async(self, persona: Persona, task: str) -> Dict:
        """
        Asenkron kod üretimi (paralel çalıştırmak için)
        
        Args:
            persona: Persona objesi
            task: Kod yazılacak görev
            
        Returns:
            Sonuç dictionary'si
        """
        # Asyncio loop içinde senkron fonksiyonu çalıştır
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            self.generate_code_for_persona, 
            persona, 
            task
        )
        return result
    
    async def generate_codes_parallel(self, task: str, personas: Optional[List[Persona]] = None) -> List[Dict]:
        """
        Birden fazla persona için paralel kod üretimi
        
        Args:
            task: Kod yazılacak görev
            personas: Persona listesi (None ise tüm persona'lar)
            
        Returns:
            Sonuç listesi
        """
        if personas is None:
            personas = self.personas
        
        # Tüm persona'lar için paralel task'lar oluştur
        tasks = [
            self.generate_code_async(persona, task)
            for persona in personas
        ]
        
        # Tüm task'ları paralel çalıştır
        results = await asyncio.gather(*tasks)
        
        return list(results)
    
    def generate_codes(self, task: str, personas: Optional[List[Persona]] = None) -> List[Dict]:
        """
        Senkron wrapper - paralel kod üretimi için
        
        Args:
            task: Kod yazılacak görev
            personas: Persona listesi (None ise tüm persona'lar)
            
        Returns:
            Sonuç listesi
        """
        return asyncio.run(self.generate_codes_parallel(task, personas))
    
    def get_personas_summary(self) -> Dict:
        """Persona'lar hakkında özet bilgi"""
        return {
            "total": len(self.personas),
            "education_count": len([p for p in self.personas if p.category == "education"]),
            "technology_count": len([p for p in self.personas if p.category == "technology"]),
            "model": self.model
        }


# Test için
if __name__ == "__main__":
    # Test kodu
    try:
        generator = CodeGenerator()
        print("✓ Code Generator başlatıldı")
        print(f"✓ Model: {generator.model}")
        print(f"✓ Toplam persona: {len(generator.personas)}")
        
        # Basit bir test
        test_task = "Fibonacci sayılarını hesaplayan bir fonksiyon yaz"
        print(f"\n🧪 Test görevi: {test_task}")
        print("⏳ Kod üretiliyor...\n")
        
        # İlk 2 persona ile test (hızlı olması için)
        results = generator.generate_codes(test_task, generator.personas[:2])
        
        for result in results:
            if result["success"]:
                print(f"✅ {result['persona_name']}: {result['tokens_used']} token")
            else:
                print(f"❌ {result['persona_name']}: {result['error']}")
        
    except ValueError as e:
        print(f"❌ Hata: {e}")
        print("💡 .env dosyasına OPENAI_API_KEY ekleyin")

