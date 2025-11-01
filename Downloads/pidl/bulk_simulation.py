"""
Bulk Simulation Runner
10 personas × N tasks × M replications = toplu kod üretimi

Araştırma için otomatik simulation çalıştırır
"""

import asyncio
from typing import List, Dict
import json
from datetime import datetime
from pathlib import Path

from personas import get_all_personas
from code_generator import CodeGenerator


class BulkSimulation:
    """Toplu simülasyon runner'ı"""
    
    def __init__(self, api_key=None):
        """
        Bulk simulation başlat
        
        Args:
            api_key: OpenAI API key
        """
        self.generator = CodeGenerator(api_key=api_key)
        self.personas = get_all_personas()
        self.results = []
    
    def run_simulation(self, tasks: List[str], replications: int = 3) -> List[Dict]:
        """
        Tüm personas için tüm tasks'ı çalıştır
        
        Args:
            tasks: Görev listesi
            replications: Her kombinasyon kaç kez
            
        Returns:
            Sonuç listesi
        """
        total_runs = len(self.personas) * len(tasks) * replications
        print(f"🔬 Başlatılıyor: {len(self.personas)} persona × {len(tasks)} task × {replications} rep = {total_runs} run")
        
        run_count = 0
        
        for persona in self.personas:
            for task in tasks:
                for rep in range(replications):
                    
                    run_count += 1
                    print(f"\n[{run_count}/{total_runs}] {persona.name} - {task[:40]}... (rep {rep+1})")
                    
                    # Kod üret
                    result = self.generator.generate_code_for_persona(persona, task)
                    
                    # Metadata ekle
                    result['run_id'] = f"{persona.id}_task{tasks.index(task)}_rep{rep}"
                    result['task'] = task
                    result['replication'] = rep + 1
                    result['timestamp'] = datetime.now().isoformat()
                    
                    self.results.append(result)
                    
                    # Progress
                    if result['success']:
                        print(f"  ✅ {result['tokens_used']} tokens")
                    else:
                        print(f"  ❌ Error: {result.get('error', 'Unknown')}")
        
        print(f"\n🎉 Tamamlandı! {len(self.results)} kod üretildi")
        print(f"  Başarılı: {sum(1 for r in self.results if r['success'])}")
        print(f"  Başarısız: {sum(1 for r in self.results if not r['success'])}")
        
        return self.results
    
    def save_results(self, filepath='data/simulation_results.json'):
        """Sonuçları kaydet"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Kaydedildi: {filepath}")
    
    def get_summary(self) -> Dict:
        """Özet istatistikler"""
        if not self.results:
            return {}
        
        successful = [r for r in self.results if r['success']]
        
        summary = {
            'total_runs': len(self.results),
            'successful': len(successful),
            'failed': len(self.results) - len(successful),
            'success_rate': len(successful) / len(self.results),
            'total_tokens': sum(r.get('tokens_used', 0) for r in successful),
            'avg_tokens_per_code': sum(r.get('tokens_used', 0) for r in successful) / len(successful) if successful else 0,
            'personas_tested': len(set(r['persona_id'] for r in self.results)),
            'tasks_tested': len(set(r.get('task', '') for r in self.results)),
            'by_persona': {}
        }
        
        # Persona bazlı
        for persona in self.personas:
            persona_results = [r for r in successful if r['persona_id'] == persona.id]
            if persona_results:
                summary['by_persona'][persona.id] = {
                    'name': persona.name,
                    'count': len(persona_results),
                    'avg_tokens': sum(r['tokens_used'] for r in persona_results) / len(persona_results)
                }
        
        return summary


# Test için
if __name__ == "__main__":
    # Örnek görevler (blockchain-education)
    sample_tasks = [
        "🎓 Solidity: Öğrenci diploması doğrulama smart contract'ı yaz",
        "📜 Solidity: Sertifika yönetim sistemi (mint, verify, revoke)",
        "💰 Solidity: Burs dağıtım ve takip smart contract'ı",
    ]
    
    print("🧪 Bulk Simulation Test\n")
    print("⚠️  Bu test, gerçek API çağrısı yapacak (maliyet: ~$2-3)")
    
    response = input("Devam etmek istiyor musunuz? (y/n): ")
    
    if response.lower() == 'y':
        sim = BulkSimulation()
        
        # Küçük test (3 task, 1 replication)
        results = sim.run_simulation(sample_tasks, replications=1)
        
        # Save
        sim.save_results('data/simulation_test_results.json')
        
        # Summary
        summary = sim.get_summary()
        print("\n📊 Özet:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    else:
        print("❌ İptal edildi")





