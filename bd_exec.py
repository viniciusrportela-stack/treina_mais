import bd_conn

FOTOS = {
    "academia": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=800&q=80",
    "academia2": "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?auto=format&fit=crop&w=800&q=80",
    "academia3": "https://images.unsplash.com/photo-1540497077202-7c8a3999166f?auto=format&fit=crop&w=800&q=80",
    "tatame": "https://images.unsplash.com/photo-1564415315949-7a0c4c73aab4?auto=format&fit=crop&w=800&q=80",
    "dojo": "https://images.unsplash.com/photo-1555597408-26bc8e548a46?auto=format&fit=crop&w=800&q=80",
    "natacao": "https://images.unsplash.com/photo-1519315901367-f34ff9154487?auto=format&fit=crop&w=800&q=80",
    "esgrima": "https://images.unsplash.com/photo-1565992441121-4367c2967103?auto=format&fit=crop&w=800&q=80",
    "pilates": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80",
}

ACADEMIAS_INICIAIS = [
    ("Smart Fit Paulista", "São Paulo", "SP", "Bela Vista", "Academia, Musculação, Funcional", "https://www.smartfit.com.br", "Rede de academias com equipamentos modernos de musculação e cardio.", FOTOS["academia"]),
    ("Bodytech Iguatemi", "São Paulo", "SP", "Jardim Paulistano", "Academia, Musculação, Natação, Pilates", "https://www.bodytech.com.br", "Estrutura completa com musculação, piscina aquecida e aulas coletivas.", FOTOS["academia2"]),
    ("Bluefit Savassi", "Belo Horizonte", "MG", "Savassi", "Academia, Musculação, Funcional", "https://www.bluefit.com.br", "Musculação, aulas coletivas e horários estendidos.", FOTOS["academia3"]),
    ("Cia Athletica Morumbi", "São Paulo", "SP", "Morumbi", "Academia, Musculação, Natação, Tatame", "https://www.ciaathletica.com.br", "Clube esportivo com musculação, lutas, natação e programas completos.", FOTOS["pilates"]),
    ("Bio Ritmo Paulista", "São Paulo", "SP", "Bela Vista", "Academia, Musculação, Funcional, Pilates", "https://www.bioritmo.com.br", "Treinos de alta performance, musculação e aulas coletivas intensas.", FOTOS["academia"]),
    ("Esporte Clube Pinheiros", "São Paulo", "SP", "Jardim Europa", "Pista de esgrima, Natação, Tatame, Esgrima", "https://www.ecp.org.br", "Clube tradicional com pistas oficiais de esgrima, tatames e parque aquático.", FOTOS["esgrima"]),
    ("Club Athletico Paulistano", "São Paulo", "SP", "Jardim América", "Pista de esgrima, Natação, Esgrima", "https://www.paulistano.org.br", "Tradição centenária na esgrima brasileira com pistas eletrônicas oficiais.", FOTOS["esgrima"]),
    ("Minas Tênis Clube", "Belo Horizonte", "MG", "Lourdes", "Natação, Tatame, Judô, Academia", "https://minastenisclube.com.br", "Complexo aquático olímpico e tatames de formação esportiva.", FOTOS["natacao"]),
    ("Sogipa", "Porto Alegre", "RS", "São João", "Dôjo, Tatame, Judô, Natação", "https://www.sogipa.com.br", "Um dos principais clubes formadores de atletas olímpicos de judô do Brasil.", FOTOS["dojo"]),
    ("Clube de Regatas do Flamengo", "Rio de Janeiro", "RJ", "Gávea", "Natação, Pista de esgrima, Tatame, Judô", "https://www.flamengo.com.br", "Escola de esportes olímpicos com piscinas, sala de esgrima e tatames.", FOTOS["tatame"]),
]


def exec(sql, params=(), fetch=None):
    conexao = bd_conn.conn()
    try:
        cursor = conexao.cursor()
        cursor.execute(sql, params)

        if fetch == "all":
            return [dict(linha) for linha in cursor.fetchall()]
        if fetch == "one":
            linha = cursor.fetchone()
            return dict(linha) if linha else None

        conexao.commit()
        return cursor.lastrowid
    finally:
        conexao.close()


def popular_iniciais():
    conexao = bd_conn.conn()
    try:
        cursor = conexao.cursor()
        cursor.executemany(
            """
            INSERT INTO academias (name, city, uf, hood, tags, url, desc, img)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ACADEMIAS_INICIAIS,
        )
        conexao.commit()
    finally:
        conexao.close()


def criar_tabela():
    exec("""
        CREATE TABLE IF NOT EXISTS academias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            uf TEXT NOT NULL,
            hood TEXT DEFAULT '',
            tags TEXT DEFAULT '',
            url TEXT NOT NULL,
            desc TEXT DEFAULT '',
            img TEXT DEFAULT ''
        )
    """)

    colunas = [c["name"] for c in exec("PRAGMA table_info(academias)", fetch="all")]
    if "img" not in colunas:
        exec("ALTER TABLE academias ADD COLUMN img TEXT DEFAULT ''")

    total = exec("SELECT COUNT(*) AS total FROM academias", fetch="one")["total"]
    if total == 0:
        popular_iniciais()