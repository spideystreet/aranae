{% macro normalize_city(city_column) %}
CASE
    -- Business districts: not standalone cities, map to their parent city
    WHEN {{ city_column }} = 'La Défense'   THEN 'Paris'

    -- Region names captured instead of a city (scraping fallback) → discard
    WHEN {{ city_column }} IN (
        'Île-de-France', 'Auvergne-Rhône-Alpes', 'Bourgogne-Franche-Comté',
        'Bretagne', 'Centre-Val de Loire', 'Corse', 'Grand Est',
        'Hauts-de-France', 'Normandie', 'Nouvelle-Aquitaine', 'Occitanie',
        'Pays de la Loire', 'Provence-Alpes-Côte d''Azur'
    ) THEN NULL

    -- Department names captured instead of a city (scraping fallback) → discard
    WHEN {{ city_column }} IN (
        'Ain', 'Aisne', 'Allier', 'Alpes-de-Haute-Provence', 'Hautes-Alpes',
        'Alpes-Maritimes', 'Ardèche', 'Ardennes', 'Ariège', 'Aube', 'Aude',
        'Aveyron', 'Bouches-du-Rhône', 'Calvados', 'Cantal', 'Charente',
        'Charente-Maritime', 'Cher', 'Corrèze', 'Corse-du-Sud', 'Haute-Corse',
        'Côte-d''Or', 'Côtes-d''Armor', 'Creuse', 'Dordogne', 'Doubs', 'Drôme',
        'Eure', 'Eure-et-Loir', 'Finistère', 'Gard', 'Haute-Garonne', 'Gers',
        'Gironde', 'Hérault', 'Ille-et-Vilaine', 'Indre', 'Indre-et-Loire',
        'Isère', 'Jura', 'Landes', 'Loir-et-Cher', 'Loire', 'Haute-Loire',
        'Loire-Atlantique', 'Loiret', 'Lot', 'Lot-et-Garonne', 'Lozère',
        'Maine-et-Loire', 'Manche', 'Marne', 'Haute-Marne', 'Mayenne',
        'Meurthe-et-Moselle', 'Meuse', 'Morbihan', 'Moselle', 'Nièvre', 'Nord',
        'Oise', 'Orne', 'Pas-de-Calais', 'Puy-de-Dôme', 'Pyrénées-Atlantiques',
        'Hautes-Pyrénées', 'Pyrénées-Orientales', 'Bas-Rhin', 'Haut-Rhin',
        'Rhône', 'Haute-Saône', 'Saône-et-Loire', 'Sarthe', 'Savoie',
        'Haute-Savoie', 'Seine-Maritime', 'Seine-et-Marne',
        'Yvelines', 'Deux-Sèvres', 'Somme', 'Tarn', 'Tarn-et-Garonne', 'Var',
        'Vaucluse', 'Vendée', 'Vienne', 'Haute-Vienne', 'Vosges', 'Yonne',
        'Territoire de Belfort', 'Essonne', 'Hauts-de-Seine', 'Seine-Saint-Denis',
        'Val-de-Marne', 'Val-d''Oise'
    ) THEN NULL

    ELSE {{ city_column }}
END
{% endmacro %}
