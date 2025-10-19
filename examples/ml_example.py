"""
Exemplo de Pipeline de Machine Learning usando Books API
Demonstra como usar a API para treinar modelos
"""
import requests
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
import warnings

warnings.filterwarnings('ignore')


class BooksMLPipeline:
    """Pipeline de ML para Books API"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.df = None
        self.label_encoder = LabelEncoder()
        
    def load_data(self, size: int = 800, random_state: int = 42):
        """Carrega dados da API"""
        print(f"📥 Carregando {size} livros da API...")
        
        response = requests.get(
            f"{self.api_url}/ml/sample",
            params={"size": size, "random_state": random_state}
        )
        response.raise_for_status()
        
        data = response.json()
        self.df = pd.DataFrame(data['data'])
        
        print(f"✅ Carregados {len(self.df)} livros")
        print(f"📊 Features: {list(self.df.columns)}")
        return self.df
    
    def preprocess_data(self):
        """Pré-processamento dos dados"""
        print("\n🔧 Pré-processamento...")
        
        # Encode categoria
        self.df['category_encoded'] = self.label_encoder.fit_transform(self.df['category'])
        
        # Criar features adicionais
        self.df['title_length'] = self.df['title'].str.len()
        self.df['desc_length'] = self.df['description'].str.len()
        self.df['has_long_desc'] = (self.df['desc_length'] > 100).astype(int)
        
        print(f"✅ Features criadas: category_encoded, title_length, desc_length, has_long_desc")
        
    def train_price_predictor(self):
        """Treina modelo para prever preços"""
        print("\n" + "=" * 80)
        print("💰 MODELO 1: Predição de Preços")
        print("=" * 80)
        
        # Features e target
        X = self.df[[
            'category_encoded',
            'rating',
            'availability_copies',
            'title_length',
            'desc_length',
            'has_long_desc'
        ]]
        y = self.df['price']
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"\n📊 Dataset:")
        print(f"  - Treino: {len(X_train)} amostras")
        print(f"  - Teste: {len(X_test)} amostras")
        
        # Treinar
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        print(f"\n🏋️  Treinando Random Forest Regressor...")
        model.fit(X_train, y_train)
        
        # Avaliar
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        print(f"\n📈 Resultados:")
        print(f"  - RMSE: £{rmse:.2f}")
        print(f"  - R² Score: {r2:.4f}")
        print(f"  - MAE: £{np.mean(np.abs(y_test - y_pred)):.2f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n🎯 Feature Importance:")
        for _, row in feature_importance.iterrows():
            bar = "█" * int(row['importance'] * 100)
            print(f"  {row['feature']:20s} {bar} {row['importance']:.4f}")
        
        # Exemplos de predição
        print(f"\n🔮 Exemplos de Predição:")
        for i in range(min(5, len(X_test))):
            real = y_test.iloc[i]
            pred = y_pred[i]
            diff = abs(real - pred)
            print(f"  Real: £{real:.2f} | Predito: £{pred:.2f} | Diff: £{diff:.2f}")
        
        return model
    
    def train_rating_classifier(self):
        """Treina modelo para classificar ratings"""
        print("\n" + "=" * 80)
        print("⭐ MODELO 2: Classificação de Ratings")
        print("=" * 80)
        
        # Features e target
        X = self.df[[
            'price',
            'category_encoded',
            'availability_copies',
            'title_length',
            'desc_length'
        ]]
        y = self.df['rating']
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"\n📊 Dataset:")
        print(f"  - Treino: {len(X_train)} amostras")
        print(f"  - Teste: {len(X_test)} amostras")
        
        # Treinar
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        print(f"\n🏋️  Treinando Random Forest Classifier...")
        model.fit(X_train, y_train)
        
        # Avaliar
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n📈 Resultados:")
        print(f"  - Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        
        # Classification report
        print(f"\n📊 Classification Report:")
        print(classification_report(y_test, y_pred, target_names=[f"{i} ⭐" for i in range(1, 6)]))
        
        # Cross-validation
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
        print(f"\n🔄 Cross-Validation (5-fold):")
        print(f"  - Scores: {[f'{s:.4f}' for s in cv_scores]}")
        print(f"  - Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        return model
    
    def analyze_correlations(self):
        """Analisa correlações entre variáveis"""
        print("\n" + "=" * 80)
        print("🔬 ANÁLISE DE CORRELAÇÕES")
        print("=" * 80)
        
        # Correlações com preço
        price_corr = self.df[[
            'price', 'rating', 'availability_copies',
            'title_length', 'desc_length', 'category_encoded'
        ]].corr()['price'].sort_values(ascending=False)
        
        print(f"\n💰 Correlação com Preço:")
        for feature, corr in price_corr.items():
            if feature != 'price':
                emoji = "📈" if corr > 0 else "📉"
                bar = "█" * int(abs(corr) * 20)
                print(f"  {emoji} {feature:25s} {bar} {corr:+.4f}")
        
        # Correlações com rating
        rating_corr = self.df[[
            'rating', 'price', 'availability_copies',
            'title_length', 'desc_length', 'category_encoded'
        ]].corr()['rating'].sort_values(ascending=False)
        
        print(f"\n⭐ Correlação com Rating:")
        for feature, corr in rating_corr.items():
            if feature != 'rating':
                emoji = "📈" if corr > 0 else "📉"
                bar = "█" * int(abs(corr) * 20)
                print(f"  {emoji} {feature:25s} {bar} {corr:+.4f}")
    
    def generate_insights(self):
        """Gera insights dos dados"""
        print("\n" + "=" * 80)
        print("💡 INSIGHTS")
        print("=" * 80)
        
        # Estatísticas por categoria
        print(f"\n📚 Top 5 Categorias por Preço Médio:")
        cat_stats = self.df.groupby('category')['price'].agg(['mean', 'count']).sort_values('mean', ascending=False)
        for cat, row in cat_stats.head().iterrows():
            print(f"  {cat:30s} £{row['mean']:6.2f} ({int(row['count'])} livros)")
        
        # Rating vs Preço
        print(f"\n⭐ Preço Médio por Rating:")
        rating_price = self.df.groupby('rating')['price'].mean().sort_index()
        for rating, price in rating_price.items():
            stars = "⭐" * rating
            print(f"  {stars:15s} £{price:.2f}")
        
        # Disponibilidade
        print(f"\n📦 Disponibilidade:")
        avail_stats = self.df['availability'].value_counts()
        for status, count in avail_stats.items():
            pct = (count / len(self.df)) * 100
            bar = "█" * int(pct / 2)
            print(f"  {status:20s} {bar} {count} ({pct:.1f}%)")


def main():
    """Função principal"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "🤖 BOOKS API - MACHINE LEARNING PIPELINE" + " " * 22 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        # Criar pipeline
        pipeline = BooksMLPipeline()
        
        # Carregar e preparar dados
        pipeline.load_data(size=800)
        pipeline.preprocess_data()
        
        # Análises
        pipeline.analyze_correlations()
        pipeline.generate_insights()
        
        # Treinar modelos
        model_price = pipeline.train_price_predictor()
        model_rating = pipeline.train_rating_classifier()
        
        # Conclusão
        print("\n" + "=" * 80)
        print("✅ Pipeline de ML concluído com sucesso!")
        print("=" * 80)
        
        print("\n💡 Próximos Passos:")
        print("  1. Salvar modelos treinados (pickle/joblib)")
        print("  2. Implementar endpoint POST /ml/predict na API")
        print("  3. Deploy dos modelos em produção")
        print("  4. Monitorar performance dos modelos")
        print("  5. Re-treinar periodicamente com novos dados")
        
        print("\n📚 Casos de Uso:")
        print("  - Sistema de recomendação de preços")
        print("  - Predição de popularidade (rating)")
        print("  - Detecção de anomalias em preços")
        print("  - Segmentação de livros (clustering)")
        print("  - Análise de sentimento em descrições")
        
        print("\n" + "=" * 80 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar à API")
        print("   Certifique-se de que a API está rodando:")
        print("   uvicorn api.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

