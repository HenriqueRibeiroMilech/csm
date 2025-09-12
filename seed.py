"""Seed script to populate template gift catalog.

Run manually: `poetry run python seed.py`

Gera um catálogo amplo de itens únicos (alvo ~300) sem variantes repetidas.
Controle via SEED_TARGET_ITEMS (default: 300). O seed é idempotente e ignora
itens que já existem por nome.
"""
import asyncio
import os
import random
import sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from backend.database import async_session_maker
from backend.models import Category, TemplateGiftItem

DISTINCT_CATALOG: dict[str, list[tuple[str, str | None]]] = {
    'Cozinha': [
        ('Jogo de Panelas Inox Completo', 'Conjunto durável para o dia a dia.'),
        ('Panela de Ferro Fundido', 'Ideal para selar e cozinhar lentamente.'),
        ('Frigideira Antiaderente', 'Não gruda e fácil de limpar.'),
        ('Assadeira Retangular Alta', 'Perfeita para lasanhas e assados.'),
        ('Conjunto de Facas de Chef', 'Cortes precisos e seguros.'),
        ('Tábua de Corte de Bambu', 'Resistente e antibacteriana.'),
        ('Liquidificador de Alto Desempenho', 'Texturas lisas para smoothies.'),
        ('Batedeira Planetária', 'Massas e cremes no ponto.'),
        ('Processador de Alimentos', 'Pica, rala e fatia com rapidez.'),
        ('Cafeteira Italiana', 'Café encorpado no fogão.'),
        ('Chaleira de Aço', 'Água quente rápida e segura.'),
        ('Jogo de Utensílios de Silicone', 'Não risca suas panelas.'),
        ('Aparelho de Jantar 42 Peças', 'Serviço completo para a casa.'),
        ('Jogo de Taças para Vinho Tinto', 'Bordas finas e elegantes.'),
        ('Jarra de Vidro com Tampa', 'Para sucos e água saborizada.'),
        ('Panela de Pressão Inox', 'Cozimento rápido e eficiente.'),
        ('Wok Tradicional', 'Salteados perfeitos e rápidos.'),
        ('Espremedor de Frutas', 'Suco fresco a qualquer hora.'),
        ('Forma para Bolo com Fundo Removível', 'Desenforma com facilidade.'),
        ('Ralador Multiuso', 'Rala fino, grosso e fatiado.'),
    ],
    'Eletrônicos': [
        ('Smart TV 55" 4K', 'Imagem nítida para filmes e séries.'),
        ('Soundbar com Subwoofer', 'Som imersivo para a sala.'),
        ('Aspirador Robô', 'Limpeza automática diária.'),
        ('Caixa de Som Bluetooth', 'Música em qualquer lugar.'),
        ('Leitor Digital Kindle', 'Leve e prático para leitura.'),
        ('Chromecast 4K', 'Streaming fácil e rápido.'),
        ('Notebook Ultrafino', 'Trabalho e estudo com mobilidade.'),
        ('Tablet 10"', 'Entretenimento e produtividade.'),
        ('Monitor 27" IPS', 'Cores vivas e ângulos amplos.'),
        ('Fone com Cancelamento de Ruído', 'Concentração total.'),
        ('Roteador Wi‑Fi 6', 'Internet rápida e estável.'),
        ('Câmera IP de Segurança', 'Monitore sua casa pelo app.'),
        ('Projetor Full HD', 'Sessão de cinema em casa.'),
        ('Smart Speaker', 'Assistente por voz e música.'),
        ('Purificador de Ar', 'Ambiente mais saudável.'),
        ('Umidificador Ultrassônico', 'Conforto em dias secos.'),
        ('Carregador Portátil', 'Bateria extra na rua.'),
        ('Hub USB‑C', 'Conecte tudo no notebook.'),
        ('Teclado Mecânico', 'Conforto e precisão ao digitar.'),
        ('Mouse Sem Fio', 'Ergonômico e silencioso.'),
    ],
    'Decoração': [
        ('Vaso de Cerâmica Texturizado', 'Peça central para mesas e aparadores.'),
        ('Conjunto de Velas Aromáticas', 'Perfuma e aconchega o ambiente.'),
        ('Quadro Abstrato', 'Toque artístico para a parede.'),
        ('Tapete Sala Felpudo', 'Conforto para os pés.'),
        ('Manta de Sofá Tricô', 'Charme e aquecimento.'),
        ('Porta‑retratos Triplo', 'Memórias sempre à vista.'),
        ('Luminária de Mesa Articulada', 'Luz direcionada para leitura.'),
        ('Espelho Redondo com Alça', 'Amplia e decora o espaço.'),
        ('Relógio de Parede Minimalista', 'Design limpo e moderno.'),
        ('Planta Artificial Realista', 'Verde sem manutenção.'),
        ('Cortina Blackout', 'Bloqueia luz e calor.'),
        ('Abajur de Cabeceira', 'Iluminação suave noturna.'),
        ('Papel de Parede Autoadesivo', 'Renova sem sujeira.'),
        ('Almofadas Decorativas Kit', 'Cores e conforto no sofá.'),
        ('Aparador de Livros', 'Organiza com estilo.'),
        ('Bandeja Decorativa Espelhada', 'Elegância na organização.'),
        ('Guirlanda de Porta', 'Boas‑vindas charmosas.'),
        ('Suporte para Plantas', 'Altura e destaque para vasos.'),
        ('Luminária de Chão Arco', 'Iluminação cênica.'),
        ('Difusor de Aromas', 'Perfuma de forma contínua.'),
    ],
    'Cama e Banho': [
        ('Jogo de Lençol 300 Fios', 'Toque macio e confortável.'),
        ('Edredom Dupla Face', 'Aconchego para noites frias.'),
        ('Colcha Matelassê', 'Acabamento elegante.'),
        ('Travesseiro Viscoelástico', 'Suporte anatômico.'),
        ('Toalha de Banho Gigante', 'Alta absorção.'),
        ('Toalha de Rosto', 'Suavidade no dia a dia.'),
        ('Tapete de Banheiro Antiderrapante', 'Segurança ao sair do banho.'),
        ('Robe Atoalhado', 'Conforto pós‑banho.'),
        ('Protetor de Colchão Impermeável', 'Proteção e higiene.'),
        ('Capa de Travesseiro', 'Conserva por mais tempo.'),
        ('Cobertor Microfibra', 'Leve e quentinho.'),
        ('Jogo de Toalhas Completo', 'Para o casal.'),
        ('Saia para Cama Box', 'Acabamento impecável.'),
        ('Cortina para Box', 'Funcional e decorativa.'),
        ('Organizador de Roupa de Cama', 'Guarda fácil e prático.'),
        ('Difusor para Banheiro', 'Cheiro agradável no ambiente.'),
        ('Pantufa Atoalhada', 'Pés quentinhos.'),
        ('Almofada de Pescoço', 'Descanso em viagens.'),
        ('Fronhas Avulsas', 'Complemento essencial.'),
        ('Toalha de Piso', 'Antiderrapante e absorvente.'),
    ],
    'Organização': [
        ('Caixa Organizadora com Tampa', 'Guarde sem poeira.'),
        ('Cesto de Roupa Suja', 'Leve e resistente.'),
        ('Sapateira Vertical', 'Aproveita o espaço.'),
        ('Cabideiro de Parede', 'Pendure e organize.'),
        ('Prateleira Modular', 'Componha como quiser.'),
        ('Organizador de Gaveta', 'Separadores ajustáveis.'),
        ('Porta‑temperos Giratório', 'Acesso rápido na cozinha.'),
        ('Porta‑joias com Divisórias', 'Protege e organiza.'),
        ('Nichos Decorativos', 'Exposição funcional.'),
        ('Caixas a Vácuo para Roupas', 'Economia de espaço.'),
        ('Carrinho Multiuso', 'Mobilidade na organização.'),
        ('Arquivo de Pastas', 'Documentos em ordem.'),
        ('Porta‑chaves', 'Nunca mais perca chaves.'),
        ('Organizador de Cabos', 'Fios sem nós.'),
        ('Porta‑especiarias', 'Culinária organizada.'),
        ('Suporte para Tampas', 'Cozinha sem bagunça.'),
        ('Ganchos Autoadesivos', 'Fixação prática.'),
        ('Cestos Aramados', 'Visibilidade do conteúdo.'),
        ('Divisória para Pratos', 'Aproveita armários.'),
        ('Suporte para Papel Toalha', 'Sempre à mão.'),
    ],
    'Bar e Vinhos': [
        ('Jogo de Taças de Cristal', 'Para brindar com elegância.'),
        ('Decanter de Vinho', 'Oxigenação perfeita.'),
        ('Saca‑rolhas Sommelier', 'Abertura sem esforço.'),
        ('Kit Bar Completo', 'Acessórios essenciais.'),
        ('Balde de Gelo Inox', 'Bebidas sempre geladas.'),
        ('Aerador de Vinho', 'Melhora os aromas.'),
        ('Coqueteleira Profissional', 'Drinks equilibrados.'),
        ('Dosador Duplo', 'Medidas precisas.'),
        ('Forma para Gelo Esfera', 'Estilo no copo.'),
        ('Jogo de Copos Old Fashioned', 'Clássicos e resistentes.'),
        ('Suporte para Garrafas', 'Armazena com charme.'),
        ('Tapete de Bar', 'Área de preparo organizada.'),
        ('Misturador de Drinks', 'Homogeneidade perfeita.'),
        ('Pegador de Gelo', 'Higiene e praticidade.'),
        ('Rolhas de Silicone', 'Conserva bebidas abertas.'),
        ('Bomba a Vácuo para Vinhos', 'Prolonga frescor.'),
        ('Bico Dosador', 'Serviço sem desperdício.'),
        ('Bandeja para Servir', 'Transporte com estilo.'),
        ('Jarra para Sangria', 'Apresentação impecável.'),
        ('Kit Marcadores de Taça', 'Identifique os copos.'),
    ],
    'Jardim': [
        ('Vaso Autoirrigável', 'Cuidados facilitados.'),
        ('Regador Metálico', 'Precisão na rega.'),
        ('Mangueira Extensível', 'Compacta e leve.'),
        ('Kit Ferramentas de Jardim', 'Plantio e manutenção.'),
        ('Jogo de Vasos de Cerâmica', 'Com diferentes alturas.'),
        ('Cortador de Grama Elétrico', 'Jardim sempre aparado.'),
        ('Tesoura de Poda', 'Cortes limpos e precisos.'),
        ('Terra Adubada', 'Crescimento saudável.'),
        ('Pá de Jardim', 'Plantio descomplicado.'),
        ('Luvas de Jardinagem', 'Proteção e conforto.'),
        ('Suporte para Mangueira', 'Organização externa.'),
        ('Sementes de Temperos', 'Horta em casa.'),
        ('Aspersor Oscilante', 'Cobertura uniforme.'),
        ('Arandelas Externas', 'Iluminação de jardim.'),
        ('Banco de Jardim', 'Descanso ao ar livre.'),
        ('Rede de Descanso', 'Relaxamento garantido.'),
        ('Lanternas Solares', 'Economia e charme noturno.'),
        ('Estátua Decorativa', 'Detalhe de personalidade.'),
        ('Tela de Sombreamento', 'Proteção para plantas.'),
        ('Composteira Doméstica', 'Reaproveite resíduos orgânicos.'),
    ],
    'Escritório': [
        ('Cadeira Ergonômica', 'Suporte lombar ajustável.'),
        ('Mesa de Escritório', 'Espaçosa e resistente.'),
        ('Luminária de Mesa LED', 'Luz fria e eficiente.'),
        ('Organizador de Mesa', 'Tudo no seu lugar.'),
        ('Suporte de Monitor', 'Altura ideal para trabalhar.'),
        ('Teclado Sem Fio', 'Menos cabos na mesa.'),
        ('Mouse Ergonômico', 'Conforto prolongado.'),
        ('Tapete para Mouse', 'Precisão no movimento.'),
        ('Gaveteiro com Rodízios', 'Armazenamento adicional.'),
        ('Painel Perfurado', 'Acessórios modulares.'),
        ('Organizador de Cabos', 'Fios controlados.'),
        ('Suporte para Notebook', 'Ângulo de digitação melhor.'),
        ('Quadro Branco', 'Anote e planeje.'),
        ('Cofre para Documentos', 'Segurança de arquivos.'),
        ('Fone com Microfone', 'Reuniões claras.'),
        ('Porta‑canetas', 'Acesso rápido e organizado.'),
        ('Estante para Livros', 'Exposição e armazenamento.'),
        ('Base Anti Fadiga', 'Conforto em estações em pé.'),
        ('Cortina Acústica', 'Redução de ruídos.'),
        ('Suporte de CPU', 'Protege do chão e poeira.'),
    ],
    'Lazer e Viagem': [
        ('Mala de Viagem com Rodas Duplas', 'Estável e silenciosa.'),
        ('Mochila Impermeável', 'Protege seus pertences.'),
        ('Garrafa Térmica Inox', 'Bebidas na temperatura certa.'),
        ('Colchonete Dobrável', 'Conforto no camping.'),
        ('Barraca 2 Pessoas', 'Fácil de montar.'),
        ('Cadeado TSA', 'Segurança nas viagens.'),
        ('Travesseiro de Pescoço', 'Descanso no avião.'),
        ('Necessaire com Divisórias', 'Higiene organizada.'),
        ('Toalha de Praia', 'Secagem rápida.'),
        ('Óculos de Sol Polarizado', 'Proteção UV garantida.'),
        ('Canga Estampada', 'Estilo à beira‑mar.'),
        ('Porta‑passaporte', 'Documentos seguros.'),
        ('Balança de Bagagem', 'Evite excedentes.'),
        ('Adaptador Universal', 'Tomadas do mundo todo.'),
        ('Cadeira de Praia', 'Leve e resistente.'),
        ('Caixa Térmica', 'Piqueniques e viagens.'),
        ('Rede Portátil', 'Relax em qualquer lugar.'),
        ('Cantil de Hidratação', 'Trilhas com água à mão.'),
        ('Bomba de Ar Manual', 'Encha infláveis facilmente.'),
        ('Kit Primeiros Socorros', 'Segurança em aventuras.'),
    ],
    'Limpeza': [
        ('Aspirador Vertical', 'Praticidade e potência.'),
        ('Mop Spray', 'Limpeza rápida de pisos.'),
        ('Rodo com Borracha', 'Secagem sem marcas.'),
        ('Esfregão Giratório', 'Remove sujeiras difíceis.'),
        ('Escova para Azulejos', 'Alcance nos cantos.'),
        ('Baldes Empilháveis', 'Organização de produtos.'),
        ('Dispensador de Detergente', 'Praticidade na pia.'),
        ('Luvas de Limpeza', 'Proteção para as mãos.'),
        ('Saco para Lavar Roupas', 'Protege peças delicadas.'),
        ('Desinfetante Concentrado', 'Higienização eficiente.'),
        ('Removedor de Manchas', 'Roupas renovadas.'),
        ('Organizador de Vassouras', 'Tudo pendurado.'),
        ('Pano Microfibra', 'Sem fiapos na limpeza.'),
        ('Escova para Garrafas', 'Alcance nas bordas.'),
        ('Cheirinho para Casa', 'Ambiente perfumado.'),
        ('Esponja Antirrisco', 'Limpa sem arranhar.'),
        ('Porta Sabão', 'Organização na lavanderia.'),
        ('Cesto de Lixo com Pedal', 'Higiene garantida.'),
        ('Água Sanitária', 'Limpeza pesada.'),
        ('Detergente Lava‑louças', 'Brilho nas louças.'),
    ],
    'Mesa Posta': [
        ('Jogo Americano de Linho', 'Elegância à mesa.'),
        ('Conjunto de Pratos Sobremesa', 'Para doces e frutas.'),
        ('Sousplat de Rattan', 'Toque natural.'),
        ('Talheres em Inox', 'Resistência e beleza.'),
        ('Garrafa para Azeite', 'Serviço preciso.'),
        ('Saleiro e Pimenteiro', 'Dupla indispensável.'),
        ('Guardanapos de Tecido', 'Refeições especiais.'),
        ('Anéis para Guardanapo', 'Acabamento sofisticado.'),
        ('Molheira de Porcelana', 'Para molhos e caldas.'),
        ('Travessa Oval', 'Servir com estilo.'),
        ('Prato Fundo', 'Massas e sopas.'),
        ('Taças para Água', 'Complemente o serviço.'),
        ('Taças para Champanhe', 'Brindes memoráveis.'),
        ('Jarra com Infusor', 'Águas aromatizadas.'),
        ('Descanso de Talheres', 'Mesa limpa e organizada.'),
        ('Cesta de Pães', 'Crocância preservada.'),
        ('Concha para Sopa', 'Serviço sem respingos.'),
        ('Colher de Sorvete', 'Bolas perfeitas.'),
        ('Afiador de Facas', 'Cortes sempre precisos.'),
        ('Suporte para Guardanapos', 'Fácil alcance.'),
    ],
    'Smart Home': [
        ('Lampada Inteligente', 'Controle por app e voz.'),
        ('Interruptor Wi‑Fi', 'Automação simples.'),
        ('Tomada Inteligente', 'Energia sob controle.'),
        ('Central de Automação', 'Integração da casa toda.'),
        ('Sensor de Movimento', 'Acione luzes automaticamente.'),
        ('Sensor de Porta e Janela', 'Alerta de abertura.'),
        ('Fechadura Eletrônica', 'Acesso por senha.'),
        ('Câmera Wi‑Fi Interna', 'Monitore ambientes.'),
        ('Campainha com Vídeo', 'Atenda pelo celular.'),
        ('Controle Universal IR', 'Domine seus eletrônicos.'),
        ('Sirene Inteligente', 'Alerta sonoro remoto.'),
        ('Tomada Medidora', 'Acompanhe consumo.'),
        ('Regador Inteligente', 'Irrigação automática.'),
        ('Cortina Automatizada', 'Conforto e praticidade.'),
        ('Abertura de Portão Wi‑Fi', 'Acesso sem controle.'),
        ('Alarme de Fumaça', 'Segurança contra incêndio.'),
        ('Detector de Vazamento', 'Previne estragos.'),
        ('HUB Zigbee', 'Maior alcance e estabilidade.'),
        ('Controle de Persiana', 'Automatize a luz natural.'),
        ('Tomada Externa Inteligente', 'Automação no jardim.'),
    ],
    'Fitness': [
        ('Colchonete de Exercícios', 'Treinos confortáveis.'),
        ('Kit Halteres Ajustáveis', 'Força progressiva.'),
        ('Faixas Elásticas', 'Treino versátil.'),
        ('Kettlebell', 'Exercícios funcionais.'),
        ('Corda de Pular', 'Cardio em qualquer lugar.'),
        ('Rolo de Liberação Miofascial', 'Recuperação muscular.'),
        ('Bola Suíça', 'Estabilidade e core.'),
        ('Barra de Porta', 'Flexões em casa.'),
        ('Anilhas de Borracha', 'Proteção do piso.'),
        ('Step Aeróbico', 'Treino de pernas e glúteos.'),
        ('Caneleira de Peso', 'Intensifique o treino.'),
        ('Luvas de Academia', 'Pegada firme.'),
        ('Garrafa Esportiva', 'Hidratação no treino.'),
        ('Toalha Esportiva', 'Secagem rápida.'),
        ('Tapete de Yoga', 'Aderência e conforto.'),
        ('Roda de Abdominais', 'Fortaleça o core.'),
        ('Suporte para Flexão', 'Ângulo ideal.'),
        ('Elíptico Compacto', 'Cardio de baixo impacto.'),
        ('Balança Digital', 'Acompanhe evolução.'),
        ('Relógio Esportivo', 'Monitoramento de atividades.'),
    ],
    'Lavanderia': [
        ('Cesto para Roupas', 'Organiza o ciclo de lavagem.'),
        ('Tábua de Passar', 'Superfície estável.'),
        ('Ferro a Vapor', 'Desamassa com eficiência.'),
        ('Varal de Chão', 'Secagem interna.'),
        ('Saco para Roupas Delicadas', 'Protege seda e renda.'),
        ('Pregadores Resistentes', 'Fixação confiável.'),
        ('Capa para Tábua', 'Melhora o deslizamento.'),
        ('Porta‑sabão', 'Armazena com praticidade.'),
        ('Porta‑amaciante', 'Dosagem precisa.'),
        ('Removedor de Pelos', 'Roupas impecáveis.'),
        ('Cesto Dobrável', 'Economiza espaço.'),
        ('Cabides Aveludados', 'Não escorregam.'),
        ('Organizador de Lavanderia', 'Tudo ao alcance.'),
        ('Escova Tira‑Pelusa', 'Renova tecidos.'),
        ('Saco para Tênis', 'Lavagem segura.'),
        ('Tapete para Lavanderia', 'Piso protegido.'),
        ('Rolo Adesivo', 'Remove poeira e pelos.'),
        ('Grade de Secagem', 'Para peças planas.'),
        ('Sabão em Pó', 'Limpeza profunda.'),
        ('Amaciante Concentrado', 'Perfume duradouro.'),
    ],
    'Pet': [
        ('Cama para Cães', 'Conforto para o pet.'),
        ('Comedouro Antiderrapante', 'Refeições sem bagunça.'),
        ('Bebedouro Fonte', 'Água sempre fresca.'),
        ('Coleira Ajustável', 'Passeios seguros.'),
        ('Guia Retrátil', 'Liberdade controlada.'),
        ('Brinquedo Mordedor', 'Alivia ansiedade.'),
        ('Arranhador para Gatos', 'Protege móveis.'),
        ('Areia Higiênica', 'Caixa sempre limpa.'),
        ('Tapete Higiênico', 'Treinamento prático.'),
        ('Shampoo para Pets', 'Higiene e cuidado.'),
        ('Escova Removedora de Pelos', 'Menos pelos pela casa.'),
        ('Ração Premium', 'Nutrição equilibrada.'),
        ('Petisco Dental', 'Saúde bucal em dia.'),
        ('Jaqueta para Pet', 'Proteção no frio.'),
        ('Cama Caverna', 'Sensação de abrigo.'),
        ('Bolsa de Transporte', 'Viagens confortáveis.'),
        ('Bebedouro Portátil', 'Passeios sem sede.'),
        ('Kit Escovação', 'Pelagem sempre bonita.'),
        ('Coleira com Plaquinha', 'Identificação rápida.'),
        ('Tapete Refrescante', 'Alívio nos dias quentes.'),
    ],
}


async def seed():
    async with async_session_maker() as session:  # type: AsyncSession
        target_total = int(os.getenv('SEED_TARGET_ITEMS', '300'))
        created = 0

        # Garante categorias
        wanted_categories = set(DISTINCT_CATALOG.keys())
        existing_categories = await session.scalars(select(Category))
        existing_by_name = {c.name: c for c in existing_categories.all()}
        for cat_name in sorted(wanted_categories):
            if cat_name not in existing_by_name:
                cat = Category(name=cat_name)
                session.add(cat)
                await session.flush()
                existing_by_name[cat_name] = cat

        # Limpa variantes antigas (opcional)
        if os.getenv('SEED_PURGE_VARIANTS', '1') == '1':
            await session.execute(
                delete(TemplateGiftItem).where(TemplateGiftItem.name.like('% - Variante %'))
            )
            await session.commit()

        # Nomes globais existentes para evitar duplicatas
        all_items = await session.scalars(select(TemplateGiftItem))
        global_names = {i.name for i in all_items.all()}

        # Embaralha categorias para diversidade na inserção
        categories = list(DISTINCT_CATALOG.keys())
        random.shuffle(categories)

        for cat_name in categories:
            if created >= target_total:
                break
            category = existing_by_name[cat_name]
            # Embaralha itens da categoria
            items = list(DISTINCT_CATALOG[cat_name])
            random.shuffle(items)
            for item_name, desc in items:
                if created >= target_total:
                    break
                if item_name in global_names:
                    continue
                session.add(
                    TemplateGiftItem(
                        name=item_name,
                        description=desc,
                        category_id=category.id,
                    )
                )
                created += 1
                global_names.add(item_name)

        await session.commit()
    print(f'Seed complete. Created {created} new template gift items (target {target_total}).')


if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed())