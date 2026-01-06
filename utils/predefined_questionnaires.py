"""
Questionnaires thérapeutiques pré-définis
pour psychothérapie, TCC, ACT, etc.
"""

def get_predefined_questionnaires():
    """Retourne la liste des questionnaires pré-définis"""

    questionnaires = []

    # 1. Échelle HAD (Hospital Anxiety and Depression scale)
    had = {
        'name': 'Échelle HAD - Hospital Anxiety and Depression',
        'short_name': 'HAD',
        'description': 'Échelle d\'auto-évaluation de l\'anxiété et de la dépression',
        'category': 'Anxiété et Dépression',
        'questions': [
            # Sous-échelle Anxiété (items impairs)
            {'id': 1, 'text': 'Je me sens tendu(e) ou énervé(e)', 'subscale': 'anxiety',
             'options': ['Jamais', 'De temps en temps', 'Souvent', 'La plupart du temps'],
             'scores': [0, 1, 2, 3]},
            {'id': 3, 'text': 'J\'ai une sensation de peur comme si quelque chose d\'horrible allait m\'arriver', 'subscale': 'anxiety',
             'options': ['Pas du tout', 'Un peu mais cela ne m\'inquiète pas', 'Oui mais ce n\'est pas trop grave', 'Oui très nettement'],
             'scores': [0, 1, 2, 3]},
            {'id': 5, 'text': 'Je me fais du souci', 'subscale': 'anxiety',
             'options': ['Très occasionnellement', 'Occasionnellement', 'Assez souvent', 'Très souvent'],
             'scores': [0, 1, 2, 3]},
            {'id': 7, 'text': 'Je peux rester tranquillement assis(e) à ne rien faire et me sentir décontracté(e)', 'subscale': 'anxiety',
             'options': ['Oui quoi qu\'il arrive', 'Oui en général', 'Rarement', 'Jamais'],
             'scores': [0, 1, 2, 3]},
            {'id': 9, 'text': 'J\'ai des sensations de peur et comme un nœud dans l\'estomac', 'subscale': 'anxiety',
             'options': ['Jamais', 'Parfois', 'Assez souvent', 'Très souvent'],
             'scores': [0, 1, 2, 3]},
            {'id': 11, 'text': 'J\'ai la bougeotte et n\'arrive pas à tenir en place', 'subscale': 'anxiety',
             'options': ['Pas du tout', 'Pas tellement', 'Un peu', 'Oui c\'est tout à fait le cas'],
             'scores': [0, 1, 2, 3]},
            {'id': 13, 'text': 'J\'éprouve des sensations soudaines de panique', 'subscale': 'anxiety',
             'options': ['Jamais', 'Pas très souvent', 'Assez souvent', 'Vraiment très souvent'],
             'scores': [0, 1, 2, 3]},
            # Sous-échelle Dépression (items pairs)
            {'id': 2, 'text': 'Je prends plaisir aux mêmes choses qu\'autrefois', 'subscale': 'depression',
             'options': ['Oui tout autant', 'Pas autant', 'Un peu seulement', 'Presque plus'],
             'scores': [0, 1, 2, 3]},
            {'id': 4, 'text': 'Je ris facilement et vois le bon côté des choses', 'subscale': 'depression',
             'options': ['Autant que par le passé', 'Plus autant qu\'avant', 'Vraiment moins qu\'avant', 'Plus du tout'],
             'scores': [0, 1, 2, 3]},
            {'id': 6, 'text': 'Je suis de bonne humeur', 'subscale': 'depression',
             'options': ['La plupart du temps', 'Assez souvent', 'Rarement', 'Jamais'],
             'scores': [0, 1, 2, 3]},
            {'id': 8, 'text': 'J\'ai l\'impression de fonctionner au ralenti', 'subscale': 'depression',
             'options': ['Jamais', 'Parfois', 'Très souvent', 'Presque toujours'],
             'scores': [0, 1, 2, 3]},
            {'id': 10, 'text': 'Je ne m\'intéresse plus à mon apparence', 'subscale': 'depression',
             'options': ['J\'y prête autant d\'attention que par le passé', 'Il se peut que je n\'y fasse plus autant attention', 'Je n\'y accorde pas autant d\'attention que je devrais', 'Plus du tout'],
             'scores': [0, 1, 2, 3]},
            {'id': 12, 'text': 'Je me réjouis d\'avance à l\'idée de faire certaines choses', 'subscale': 'depression',
             'options': ['Autant qu\'avant', 'Un peu moins qu\'avant', 'Bien moins qu\'avant', 'Presque jamais'],
             'scores': [0, 1, 2, 3]},
            {'id': 14, 'text': 'Je peux prendre plaisir à un bon livre ou à une bonne émission de radio ou de télévision', 'subscale': 'depression',
             'options': ['Souvent', 'Parfois', 'Rarement', 'Très rarement'],
             'scores': [0, 1, 2, 3]}
        ],
        'scoring_method': '''
Cotation HAD:
- Score anxiété (A): somme des items 1, 3, 5, 7, 9, 11, 13
- Score dépression (D): somme des items 2, 4, 6, 8, 10, 12, 14

Interprétation pour chaque sous-échelle:
- 0-7: Absence de symptomatologie
- 8-10: Symptomatologie douteuse
- 11-21: Symptomatologie certaine
        ''',
        'interpretation': '''
L'échelle HAD permet d'évaluer l'anxiété et la dépression chez les patients.
Chaque sous-échelle (A et D) est cotée de 0 à 21.
Un score ≥ 8 indique une symptomatologie probable.
Un score ≥ 11 indique une symptomatologie certaine nécessitant une prise en charge.
        '''
    }
    questionnaires.append(had)

    # 2. Inventaire de Beck pour la Dépression (BDI-II - version simplifiée)
    beck = {
        'name': 'Inventaire de Beck pour la Dépression (BDI-II)',
        'short_name': 'BDI-II',
        'description': 'Auto-questionnaire évaluant l\'intensité de la dépression',
        'category': 'Dépression',
        'questions': [
            {'id': 1, 'text': 'Tristesse', 'subscale': 'depression',
             'options': [
                 'Je ne me sens pas triste',
                 'Je me sens très souvent triste',
                 'Je suis tout le temps triste',
                 'Je suis si triste ou si malheureux(se) que ce n\'est pas supportable'
             ],
             'scores': [0, 1, 2, 3]},
            {'id': 2, 'text': 'Pessimisme', 'subscale': 'depression',
             'options': [
                 'Je ne suis pas découragé(e) face à mon avenir',
                 'Je me sens plus découragé(e) qu\'avant face à mon avenir',
                 'Je ne m\'attends pas à ce que les choses s\'arrangent pour moi',
                 'J\'ai le sentiment que mon avenir est sans espoir et qu\'il ne peut qu\'empirer'
             ],
             'scores': [0, 1, 2, 3]},
            {'id': 3, 'text': 'Échecs dans le passé', 'subscale': 'depression',
             'options': [
                 'Je n\'ai pas le sentiment d\'avoir échoué dans la vie',
                 'J\'ai échoué plus souvent que je n\'aurais dû',
                 'Quand je pense au passé, je constate un grand nombre d\'échecs',
                 'J\'ai le sentiment d\'avoir complètement raté ma vie'
             ],
             'scores': [0, 1, 2, 3]},
            {'id': 4, 'text': 'Perte de plaisir', 'subscale': 'depression',
             'options': [
                 'J\'éprouve toujours autant de plaisir qu\'avant aux choses qui me plaisent',
                 'Je n\'éprouve plus autant de plaisir aux choses qu\'avant',
                 'J\'éprouve très peu de plaisir aux choses qui me plaisaient habituellement',
                 'Je n\'éprouve aucun plaisir aux choses qui me plaisaient habituellement'
             ],
             'scores': [0, 1, 2, 3]},
            {'id': 5, 'text': 'Sentiments de culpabilité', 'subscale': 'depression',
             'options': [
                 'Je ne me sens pas particulièrement coupable',
                 'Je me sens coupable pour bien des choses que j\'ai faites ou que j\'aurais dû faire',
                 'Je me sens coupable la plupart du temps',
                 'Je me sens tout le temps coupable'
             ],
             'scores': [0, 1, 2, 3]}
        ],
        'scoring_method': '''
Cotation BDI-II:
- Score total: somme de tous les items (0-63 pour la version complète)
- Cette version simplifiée ne contient que 5 items à titre d'exemple

Interprétation (version complète 21 items):
- 0-13: Dépression minimale
- 14-19: Dépression légère
- 20-28: Dépression modérée
- 29-63: Dépression sévère
        ''',
        'interpretation': '''
Le BDI-II est un outil de référence pour évaluer la sévérité de la dépression.
Cette version simplifiée ne permet qu'une estimation partielle.
        '''
    }
    questionnaires.append(beck)

    # 3. Échelle d'acceptation et d'action (AAQ-II) pour ACT
    aaq = {
        'name': 'Questionnaire d\'Acceptation et d\'Action (AAQ-II)',
        'short_name': 'AAQ-II',
        'description': 'Évalue la flexibilité psychologique et l\'évitement expérientiel',
        'category': 'ACT - Flexibilité psychologique',
        'questions': [
            {'id': 1, 'text': 'Mes expériences et souvenirs douloureux m\'empêchent de mener une vie qui compte pour moi',
             'options': ['Jamais vrai', 'Rarement vrai', 'Parfois vrai', 'Souvent vrai', 'Toujours vrai'],
             'scores': [1, 2, 3, 4, 5]},
            {'id': 2, 'text': 'J\'ai peur de mes sentiments',
             'options': ['Jamais vrai', 'Rarement vrai', 'Parfois vrai', 'Souvent vrai', 'Toujours vrai'],
             'scores': [1, 2, 3, 4, 5]},
            {'id': 3, 'text': 'Je m\'inquiète de ne pas être capable de contrôler mes inquiétudes et mes sentiments',
             'options': ['Jamais vrai', 'Rarement vrai', 'Parfois vrai', 'Souvent vrai', 'Toujours vrai'],
             'scores': [1, 2, 3, 4, 5]},
            {'id': 4, 'text': 'Mes souvenirs douloureux m\'empêchent d\'avoir une vie épanouissante',
             'options': ['Jamais vrai', 'Rarement vrai', 'Parfois vrai', 'Souvent vrai', 'Toujours vrai'],
             'scores': [1, 2, 3, 4, 5]},
            {'id': 5, 'text': 'Les émotions causent des problèmes dans ma vie',
             'options': ['Jamais vrai', 'Rarement vrai', 'Parfois vrai', 'Souvent vrai', 'Toujours vrai'],
             'scores': [1, 2, 3, 4, 5]},
            {'id': 6, 'text': 'Il me semble que la plupart des gens gèrent leur vie mieux que moi',
             'options': ['Jamais vrai', 'Rarement vrai', 'Parfois vrai', 'Souvent vrai', 'Toujours vrai'],
             'scores': [1, 2, 3, 4, 5]},
            {'id': 7, 'text': 'Les inquiétudes interfèrent avec ma réussite',
             'options': ['Jamais vrai', 'Rarement vrai', 'Parfois vrai', 'Souvent vrai', 'Toujours vrai'],
             'scores': [1, 2, 3, 4, 5]}
        ],
        'scoring_method': '''
Cotation AAQ-II:
- Score total: somme de tous les items (7-35)
- Plus le score est élevé, plus l'inflexibilité psychologique est importante

Interprétation:
- Score élevé (>24): Forte inflexibilité psychologique, évitement expérientiel important
- Score moyen (17-24): Inflexibilité modérée
- Score faible (<17): Bonne flexibilité psychologique
        ''',
        'interpretation': '''
L'AAQ-II mesure l'inflexibilité psychologique et l'évitement expérientiel,
des concepts centraux en thérapie ACT (Acceptance and Commitment Therapy).
Un score élevé suggère des difficultés à accepter les expériences internes désagréables.
        '''
    }
    questionnaires.append(aaq)

    # 4. Échelle de Pleine Conscience (MAAS - Mindful Attention Awareness Scale)
    maas = {
        'name': 'Échelle de Pleine Conscience (MAAS)',
        'short_name': 'MAAS',
        'description': 'Évalue la capacité à porter attention au moment présent',
        'category': 'Pleine conscience',
        'questions': [
            {'id': 1, 'text': 'Je peux vivre une émotion et ne m\'en rendre compte qu\'un certain temps après',
             'options': ['Presque toujours', 'Très fréquemment', 'Assez fréquemment', 'Assez peu fréquemment', 'Très peu fréquemment', 'Presque jamais'],
             'scores': [1, 2, 3, 4, 5, 6]},
            {'id': 2, 'text': 'Je casse ou renverse des choses par négligence, par inattention ou parce que je pense à autre chose',
             'options': ['Presque toujours', 'Très fréquemment', 'Assez fréquemment', 'Assez peu fréquemment', 'Très peu fréquemment', 'Presque jamais'],
             'scores': [1, 2, 3, 4, 5, 6]},
            {'id': 3, 'text': 'J\'ai des difficultés à rester concentré(e) sur ce qui se passe dans le présent',
             'options': ['Presque toujours', 'Très fréquemment', 'Assez fréquemment', 'Assez peu fréquemment', 'Très peu fréquemment', 'Presque jamais'],
             'scores': [1, 2, 3, 4, 5, 6]},
            {'id': 4, 'text': 'J\'ai tendance à marcher rapidement pour me rendre là où je veux aller, sans prêter attention à ce qui se passe durant le trajet',
             'options': ['Presque toujours', 'Très fréquemment', 'Assez fréquemment', 'Assez peu fréquemment', 'Très peu fréquemment', 'Presque jamais'],
             'scores': [1, 2, 3, 4, 5, 6]},
            {'id': 5, 'text': 'J\'ai tendance à ne pas remarquer des tensions physiques ou un inconfort physique jusqu\'à ce qu\'ils deviennent criants',
             'options': ['Presque toujours', 'Très fréquemment', 'Assez fréquemment', 'Assez peu fréquemment', 'Très peu fréquemment', 'Presque jamais'],
             'scores': [1, 2, 3, 4, 5, 6]}
        ],
        'scoring_method': '''
Cotation MAAS:
- Score total: moyenne de tous les items (1-6)
- Plus le score est élevé, plus le niveau de pleine conscience est important

Interprétation:
- Score élevé (>4.5): Bonne capacité de pleine conscience
- Score moyen (3-4.5): Capacité modérée
- Score faible (<3): Faible capacité de pleine conscience, tendance à l'inattention
        ''',
        'interpretation': '''
La MAAS évalue la disposition à être attentif et conscient de l'expérience du moment présent
dans la vie quotidienne. Les scores élevés indiquent une plus grande conscience et attention.
        '''
    }
    questionnaires.append(maas)

    # 5. Questionnaire simple de suivi thérapeutique
    suivi = {
        'name': 'Questionnaire de Suivi Thérapeutique',
        'short_name': 'SUIVI',
        'description': 'Évaluation rapide du bien-être et de la progression',
        'category': 'Suivi général',
        'questions': [
            {'id': 1, 'text': 'Comment évaluez-vous votre humeur cette semaine ?',
             'options': ['Très mauvaise', 'Mauvaise', 'Neutre', 'Bonne', 'Très bonne'],
             'scores': [1, 2, 3, 4, 5]},
            {'id': 2, 'text': 'Comment évaluez-vous votre niveau d\'anxiété cette semaine ?',
             'options': ['Très élevé', 'Élevé', 'Moyen', 'Faible', 'Très faible'],
             'scores': [5, 4, 3, 2, 1]},
            {'id': 3, 'text': 'Avez-vous pratiqué les exercices proposés lors de la dernière séance ?',
             'options': ['Pas du tout', 'Rarement', 'Parfois', 'Souvent', 'Tous les jours'],
             'scores': [1, 2, 3, 4, 5]},
            {'id': 4, 'text': 'Comment évaluez-vous la qualité de votre sommeil ?',
             'options': ['Très mauvaise', 'Mauvaise', 'Moyenne', 'Bonne', 'Très bonne'],
             'scores': [1, 2, 3, 4, 5]},
            {'id': 5, 'text': 'Sentez-vous des progrès depuis le début de la thérapie ?',
             'options': ['Aucun progrès', 'Peu de progrès', 'Quelques progrès', 'Progrès significatifs', 'Progrès très importants'],
             'scores': [1, 2, 3, 4, 5]}
        ],
        'scoring_method': '''
Cotation Suivi:
- Score total: somme de tous les items (5-25)
- Ce questionnaire permet un suivi rapide de l'évolution du patient

Interprétation:
- Score élevé (>18): Bonne évolution
- Score moyen (12-18): Évolution modérée
- Score faible (<12): Difficultés persistantes
        ''',
        'interpretation': '''
Ce questionnaire permet un suivi régulier de l'évolution du patient
entre les séances et d'identifier rapidement les domaines nécessitant attention.
        '''
    }
    questionnaires.append(suivi)

    return questionnaires
