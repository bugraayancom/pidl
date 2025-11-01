"""
Multi-LLM Karşılaştırma Motoru
OpenAI, Google Gemini, Anthropic Claude, X.AI Grok desteği

Araştırma Sorusu: Farklı LLM'ler aynı persona karakteristiğini 
ne kadar iyi yansıtıyor ve performans farkları nedir?
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# LLM imports
import openai

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from personas import Persona

load_dotenv()


class MultiLLMEngine:
    """
    Çoklu LLM desteği ile kod üretimi
    
    Desteklenen modeller:
    - OpenAI: gpt-4o, gpt-4o-mini, gpt-4-turbo
    - Anthropic: claude-3-opus, claude-3-sonnet, claude-3-haiku
    - Google: gemini-pro, gemini-1.5-pro
    - X.AI: grok-beta
    """
    
    # Model fiyatlandırması (1M token başına $)
    PRICING = {
        "gpt-4o": {"input": 5.00, "output": 15.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "claude-3-opus": {"input": 15.00, "output": 75.00},
        "claude-3-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
        "gemini-pro": {"input": 0.50, "output": 1.50},
        "gemini-1.5-pro": {"input": 3.50, "output": 10.50},
        "grok-beta": {"input": 5.00, "output": 15.00}
    }
    
    def __init__(self):
        """Multi-LLM engine başlat"""
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")
        self.grok_key = os.getenv("GROK_API_KEY")
        
        # Clients
        self.openai_client = None
        self.anthropic_client = None
        self.google_client = None
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """LLM client'larını başlat"""
        # OpenAI
        if self.openai_key:
            try:
                self.openai_client = openai.OpenAI(api_key=self.openai_key)
            except Exception as e:
                print(f"OpenAI client başlatılamadı: {e}")
        
        # Anthropic - Sadece geçerli API key varsa başlat
        if self.anthropic_key and self.anthropic_key != "your_anthropic_api_key_here" and ANTHROPIC_AVAILABLE:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
            except Exception as e:
                print(f"Anthropic client başlatılamadı: {e}")
                self.anthropic_client = None
        
        # Google - Sadece geçerli API key varsa başlat
        if self.google_key and self.google_key != "your_google_key_here" and GOOGLE_AVAILABLE:
            try:
                genai.configure(api_key=self.google_key)
                self.google_client = genai
            except Exception as e:
                print(f"Google client başlatılamadı: {e}")
                self.google_client = None
    
    def get_available_models(self) -> List[Dict]:
        """Kullanılabilir modelleri listele"""
        models = []
        
        if self.openai_client:
            models.extend([
                {"provider": "OpenAI", "model": "gpt-4o", "status": "✅"},
                {"provider": "OpenAI", "model": "gpt-4o-mini", "status": "✅"},
                {"provider": "OpenAI", "model": "gpt-4-turbo", "status": "✅"}
            ])
        
        if self.anthropic_client:
            models.extend([
                {"provider": "Anthropic", "model": "claude-3-opus-20240229", "status": "✅"},
                {"provider": "Anthropic", "model": "claude-3-sonnet-20240229", "status": "✅"},
                {"provider": "Anthropic", "model": "claude-3-haiku-20240307", "status": "✅"}
            ])
        
        if self.google_client:
            models.extend([
                {"provider": "Google", "model": "gemini-pro", "status": "✅"},
                {"provider": "Google", "model": "gemini-1.5-pro", "status": "✅"}
            ])
        
        # Grok (OpenAI compatible API)
        if self.grok_key:
            models.append(
                {"provider": "X.AI", "model": "grok-beta", "status": "✅"}
            )
        
        return models
    
    def generate_with_openai(self, model: str, system_prompt: str, 
                            user_prompt: str) -> Dict:
        """OpenAI ile kod üret"""
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            code = response.choices[0].message.content.strip()
            
            # Kod bloklarını temizle
            if code.startswith("```python"):
                code = code[9:]
            elif code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]
            code = code.strip()
            
            return {
                "success": True,
                "code": code,
                "tokens": response.usage.total_tokens,
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "model": model,
                "provider": "OpenAI"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model,
                "provider": "OpenAI"
            }
    
    def generate_with_anthropic(self, model: str, system_prompt: str,
                               user_prompt: str) -> Dict:
        """Anthropic Claude ile kod üret"""
        try:
            if not self.anthropic_client:
                return {"success": False, "error": "Anthropic client yok"}
            
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=2000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            code = response.content[0].text.strip()
            
            # Kod bloklarını temizle
            if code.startswith("```python"):
                code = code[9:]
            elif code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]
            code = code.strip()
            
            return {
                "success": True,
                "code": code,
                "tokens": response.usage.input_tokens + response.usage.output_tokens,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "model": model,
                "provider": "Anthropic"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model,
                "provider": "Anthropic"
            }
    
    def generate_with_google(self, model: str, system_prompt: str,
                            user_prompt: str) -> Dict:
        """Google Gemini ile kod üret"""
        try:
            if not self.google_client:
                return {"success": False, "error": "Google client yok"}
            
            model_obj = self.google_client.GenerativeModel(model)
            
            # Gemini system instruction ile çalışır
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = model_obj.generate_content(full_prompt)
            
            code = response.text.strip()
            
            # Kod bloklarını temizle
            if code.startswith("```python"):
                code = code[9:]
            elif code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]
            code = code.strip()
            
            # Gemini token sayısını tam vermez, tahmin edelim
            estimated_tokens = len(full_prompt.split()) + len(code.split())
            
            return {
                "success": True,
                "code": code,
                "tokens": estimated_tokens,
                "input_tokens": len(full_prompt.split()),
                "output_tokens": len(code.split()),
                "model": model,
                "provider": "Google"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model,
                "provider": "Google"
            }
    
    def generate_with_grok(self, model: str, system_prompt: str,
                          user_prompt: str) -> Dict:
        """X.AI Grok ile kod üret (OpenAI compatible)"""
        try:
            if not self.grok_key:
                return {"success": False, "error": "Grok API key yok"}
            
            # Grok OpenAI compatible API kullanır
            client = openai.OpenAI(
                api_key=self.grok_key,
                base_url="https://api.x.ai/v1"
            )
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            code = response.choices[0].message.content.strip()
            
            # Kod bloklarını temizle
            if code.startswith("```python"):
                code = code[9:]
            elif code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]
            code = code.strip()
            
            return {
                "success": True,
                "code": code,
                "tokens": response.usage.total_tokens,
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "model": model,
                "provider": "X.AI"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model,
                "provider": "X.AI"
            }
    
    def generate_multi_llm(self, persona: Persona, persona_prompt: str,
                          models: List[str]) -> List[Dict]:
        """
        Aynı persona ve prompt ile birden fazla LLM'den kod üret
        
        Args:
            persona: Persona objesi
            persona_prompt: Persona'nın yazdığı özel prompt
            models: Kullanılacak model listesi
            
        Returns:
            Her model için sonuç listesi
        """
        results = []
        
        # Tam user prompt
        user_prompt = f"""
Görev için senin perspektifinden hazırladığın prompt:
"{persona_prompt}"

Bu prompt'a göre Python kodu yaz. Kodun:
- Çalışabilir ve test edilebilir olmalı
- Kendi uzmanlık alanına göre yaklaşmalısın
- Gerekli import'ları ekle

Sadece Python kodunu yaz, başka açıklama ekleme.
"""
        
        for model in models:
            # Provider'ı belirle
            if model.startswith("gpt"):
                result = self.generate_with_openai(model, persona.system_prompt, user_prompt)
            elif model.startswith("claude"):
                result = self.generate_with_anthropic(model, persona.system_prompt, user_prompt)
            elif model.startswith("gemini"):
                result = self.generate_with_google(model, persona.system_prompt, user_prompt)
            elif model.startswith("grok"):
                result = self.generate_with_grok(model, persona.system_prompt, user_prompt)
            else:
                result = {"success": False, "error": "Bilinmeyen model"}
            
            # Persona bilgilerini ekle
            result.update({
                "persona_id": persona.id,
                "persona_name": persona.name,
                "persona_role": persona.role,
                "category": persona.category,
                "avatar": persona.avatar,
                "persona_prompt": persona_prompt
            })
            
            results.append(result)
        
        return results
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """
        Maliyet hesapla
        
        Args:
            input_tokens: Input token sayısı
            output_tokens: Output token sayısı
            model: Model adı
            
        Returns:
            Toplam maliyet ($)
        """
        # Model ismini normalize et (versiyonları kaldır)
        model_key = model
        if "claude-3" in model:
            if "opus" in model:
                model_key = "claude-3-opus"
            elif "sonnet" in model:
                model_key = "claude-3-sonnet"
            elif "haiku" in model:
                model_key = "claude-3-haiku"
        elif "gemini" in model:
            if "1.5" in model:
                model_key = "gemini-1.5-pro"
            else:
                model_key = "gemini-pro"
        
        pricing = self.PRICING.get(model_key, {"input": 1.0, "output": 3.0})
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost


# Test için
if __name__ == "__main__":
    engine = MultiLLMEngine()
    
    available = engine.get_available_models()
    
    print("🤖 Kullanılabilir LLM Modelleri:\n")
    for model in available:
        print(f"{model['status']} {model['provider']:12s} - {model['model']}")
    
    print(f"\n✅ Toplam {len(available)} model kullanılabilir")

