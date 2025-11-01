"""
Data Exporter & Statistical Analyzer
Araştırma verilerni CSV, Excel, SPSS formatına export eder
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime


class DataExporter:
    """Veri export ve analiz sistemi"""
    
    def __init__(self):
        """Exporter başlat"""
        pass
    
    def export_synthetic_users(self, users: list, format='csv'):
        """
        Synthetic users'ı export et
        
        Args:
            users: User list
            format: 'csv', 'excel', 'json'
        """
        df = pd.DataFrame(users)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'csv':
            filepath = f'data/export/synthetic_users_{timestamp}.csv'
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
        elif format == 'excel':
            filepath = f'data/export/synthetic_users_{timestamp}.xlsx'
            df.to_excel(filepath, index=False, engine='openpyxl')
        elif format == 'json':
            filepath = f'data/export/synthetic_users_{timestamp}.json'
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Export edildi: {filepath}")
        return filepath
    
    def export_matching_results(self, matching_data: list, format='csv'):
        """Matching sonuçlarını export et"""
        df = pd.DataFrame(matching_data)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f'data/export/matching_results_{timestamp}.{format}'
        
        if format == 'csv':
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
        elif format in ['xlsx', 'excel']:
            df.to_excel(filepath.replace(format, 'xlsx'), index=False)
        
        print(f"✅ Matching results export edildi: {filepath}")
        return filepath
    
    def generate_spss_syntax(self, csv_file: str, output_file: str = None):
        """
        SPSS import syntax oluştur
        
        Args:
            csv_file: CSV dosya yolu
            output_file: SPSS syntax dosyası (.sps)
        """
        if output_file is None:
            output_file = csv_file.replace('.csv', '.sps')
        
        syntax = f"""* SPSS Import Syntax for PIDL Research Data
* Generated: {datetime.now()}

GET DATA
  /TYPE=TXT
  /FILE='{csv_file}'
  /ENCODING='UTF8'
  /DELIMITERS=","
  /QUALIFIER='"'
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
  /VARIABLES=
    user_id A20
    technical_score F8.2
    educational_score F8.2
    recommendation_score F8.4
    mode A20
    persona_category A20.

EXECUTE.

* Define value labels
VALUE LABELS mode
  'similarity' 'Benzerlik Bazlı'
  'complementary' 'Tamamlayıcı Bazlı'.

* Compute derived variables
COMPUTE overall_score = (technical_score + educational_score) / 2.
EXECUTE.

SAVE OUTFILE='pidl_data.sav'.
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(syntax)
        
        print(f"✅ SPSS syntax oluşturuldu: {output_file}")
        return output_file
    
    def create_summary_statistics(self, data: pd.DataFrame) -> Dict:
        """Özet istatistikler hesapla"""
        summary = {
            'n': len(data),
            'descriptives': {
                'technical_score': {
                    'mean': data['user_tech_score'].mean(),
                    'std': data['user_tech_score'].std(),
                    'min': data['user_tech_score'].min(),
                    'max': data['user_tech_score'].max(),
                    'median': data['user_tech_score'].median()
                },
                'educational_score': {
                    'mean': data['user_edu_score'].mean(),
                    'std': data['user_edu_score'].std(),
                    'min': data['user_edu_score'].min(),
                    'max': data['user_edu_score'].max(),
                    'median': data['user_edu_score'].median()
                },
                'recommendation_score': {
                    'mean': data['recommendation_score'].mean(),
                    'std': data['recommendation_score'].std()
                }
            },
            'correlations': {
                'tech_edu': data[['user_tech_score', 'user_edu_score']].corr().iloc[0, 1]
            },
            'mode_comparison': {
                'similarity_mean': data[data['mode']=='similarity']['recommendation_score'].mean(),
                'complementary_mean': data[data['mode']=='complementary']['recommendation_score'].mean(),
                'difference': data[data['mode']=='complementary']['recommendation_score'].mean() - 
                             data[data['mode']=='similarity']['recommendation_score'].mean()
            }
        }
        
        return summary


# Test için
if __name__ == "__main__":
    print("🧪 Matching Tester Quick Test\n")
    
    # 10 user oluştur
    gen = SyntheticUserGenerator(seed=42)
    users = gen.generate_users(n_per_stratum=1)
    
    # Matching test
    tester = MatchingTester()
    results = tester.test_all_matchings(users)
    
    # Export
    Path('data/export').mkdir(parents=True, exist_ok=True)
    tester.export_matching_results(results, format='csv')
    
    # Summary
    df = pd.DataFrame(results)
    summary = tester.create_summary_statistics(df)
    
    print("\n📊 Summary Statistics:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    print("\n✅ Test tamamlandı!")





