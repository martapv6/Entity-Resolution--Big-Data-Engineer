# Entity-Resolution--Big-Data-Engineer
Scopul proiectului este identificarea și gruparea companiilor care apar de mai multe ori în baza de date, dar cu informații ușor diferite (problema de tip entity resolution). Rezultatul final este un set de companii unice, obținut prin calculul unui scor de unicitate și aplicarea unui algoritm de grupare bazat pe asemănare (fuzzy matching).
Etapele proiectului
Pasul 1 – Intelegerea datelor
Am analizat fisierul de date pentru a vedea volumul, structura si distributia valorilor.
La inceput am testat unicitatea pe codul postal, dar am observat ca nu este suficient pentru a diferentia corect companiile.
Am continuat prin a verifica valorile unice si duplicatele pentru mai multe coloane, ignorand valorile nule.
Pentru a vedea mai clar rezultatele, am salvat unele extrageri si in fisiere JSON.

Pasul 2 – Alegerea coloanelor relevante
Am ales un set de coloane importante care pot ajuta la identificarea companiilor unice, precum:
company_name
company_legal_names
website_domain
primary_email
primary_phone
linkedin_url
main_country_code
main_city
main_postcode
main_street
main_latitude
main_longitude
year_founded
naics_2022_primary_code
main_industry
main_sector

Am exclus coloanele descriptive (de exemplu, long_description, business_tags, revenue, employee_count) care nu ajuta direct la identificarea entitatii.

Pasul 3 – Calcularea scorului de unicitate

Pentru fiecare coloana am calculat un scor de unicitate, care arata cat de rara este valoarea respectiva in setul de date:
daca o valoare apare o singura data → scor mare (1.0)
daca apare de mai multe ori → scor mai mic
daca valoarea lipseste → scor 0
Am impartit coloanele in trei categorii:
coloane primare (cele mai importante)
coloane secundare
coloane de context

Scorul final al unei companii (unicity_score) se calculeaza ca medie ponderata:
0.5 * scorul primar + 0.3 * scorul secundar + 0.2 * scorul de context.

Pasul 4 – Gruparea companiilor similare
Dupa ce am obtinut scorul de unicitate, am trecut la gruparea companiilor care par sa reprezinte aceeasi entitate.
Am curatat si normalizat numele companiilor (litere mici, fara forme juridice ca SRL, LTD, INC).
Am folosit campuri directe precum website_domain, email sau telefon pentru a uni inregistrarile identice.
Pentru restul, am aplicat un algoritm de fuzzy matching folosind biblioteca rapidfuzz.
Compara denumirile companiilor si calculeaza un scor de asemanare (token_set_ratio).
Daca scorul este peste 92%, companiile sunt puse in acelasi grup.
Am folosit o structura union-find pentru a reuni toate companiile similare intr-un grup unic (fuzzy_group_id).
Din fiecare grup, am pastrat doar compania cu cel mai mare unicity_score.

Rezultate finale:
Proiectul genereaza doua fisiere:
-veridion_with_fuzzy_groups.parquet
Contine toate companiile din setul original si grupul din care fac parte (fuzzy_group_id).
-veridion_fuzzy_unique.parquet
Contine cate o singura companie unica pentru fiecare grup, adica setul curatat de duplicate.

Tehnologii folosite:
Python
Pandas
PyArrow
RapidFuzz
Numpy

Concluzie
Prin combinarea unui scor de unicitate cu o etapa de fuzzy matching, am reusit sa:
detectez duplicate chiar si atunci cand datele difera usor;
evit unificarea companiilor care au acelasi nume dar atribute complet diferite;
obtin o baza de date finala curata, cu fiecare companie prezenta o singura data.
