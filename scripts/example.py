#!/usr/bin/env python3
"""
Yksinkertainen esimerkki embedding-toiminnosta
"""

def main():
    print("🧪 LLMFixU Embedding-esimerkki")
    print("=============================")
    
    # Simuloi embedding-prosessi
    sample_texts = [
        "Yrityksen tietoturvakäytännöt ovat ajantasaiset ja noudattavat ISO 27001 -standardia.",
        "GDPR-vaatimustenmukaisuus on varmistettu kaikissa asiakastietoja käsittelevissä prosesseissa.", 
        "Henkilöstön koulutussuunnitelma sisältää cybersecurity-osaamisen kehittämisen.",
        "Varmuuskopiointijärjestelmä on testattu ja toddettu toimivaksi viimeisen auditoinnin yhteydessä."
    ]
    
    print("Esimerkkidokumentteja:")
    for i, text in enumerate(sample_texts, 1):
        print(f"{i}. {text}")
    
    print("\nTämä esimerkki näyttäisi miten dokumentit tallennettaisiin ChromaDB:hen.")
    print("Käytä 'python scripts/embed.py' tallentaaksesi oikeita dokumentteja.")
    print("Ja 'python scripts/query.py' hakiaksesi niitä.")

if __name__ == "__main__":
    main()