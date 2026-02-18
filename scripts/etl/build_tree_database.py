"""Orchestrate ETL processing: merge EU-Forest, Med DB, EU-Trees4F into unified tree_species.json."""

from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Research-based defaults for species enrichment
SPECIES_DEFAULTS: dict[str, dict[str, object]] = {
    "Quercus robur": {"common_name": "English Oak", "soil_ph_min": 4.5, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "shade", "max_height_m": 35.0, "maintenance_level": "low", "attributes": ["Deciduous", "Native", "Wildlife-friendly"]},
    "Quercus ilex": {"common_name": "Holm Oak", "soil_ph_min": 5.0, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "shade", "max_height_m": 25.0, "maintenance_level": "low", "attributes": ["Evergreen", "Drought-tolerant"]},
    "Quercus petraea": {"common_name": "Sessile Oak", "soil_ph_min": 4.5, "soil_ph_max": 7.0, "drought_tolerant": False, "primary_use": "shade", "max_height_m": 30.0, "maintenance_level": "low", "attributes": ["Deciduous", "Native"]},
    "Quercus pubescens": {"common_name": "Downy Oak", "soil_ph_min": 5.5, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "shade", "max_height_m": 20.0, "maintenance_level": "low", "attributes": ["Deciduous", "Drought-tolerant"]},
    "Quercus suber": {"common_name": "Cork Oak", "soil_ph_min": 4.5, "soil_ph_max": 7.0, "drought_tolerant": True, "primary_use": "shade", "max_height_m": 20.0, "maintenance_level": "low", "attributes": ["Evergreen", "Drought-tolerant"]},
    "Quercus cerris": {"common_name": "Turkey Oak", "soil_ph_min": 5.0, "soil_ph_max": 7.5, "drought_tolerant": True, "primary_use": "shade", "max_height_m": 35.0, "maintenance_level": "low", "attributes": ["Deciduous"]},
    "Quercus frainetto": {"common_name": "Hungarian Oak", "soil_ph_min": 5.0, "soil_ph_max": 7.5, "drought_tolerant": True, "primary_use": "shade", "max_height_m": 30.0, "maintenance_level": "low", "attributes": ["Deciduous"]},
    "Fagus sylvatica": {"common_name": "European Beech", "soil_ph_min": 4.0, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "shade", "max_height_m": 40.0, "maintenance_level": "low", "attributes": ["Deciduous", "Native"]},
    "Betula pendula": {"common_name": "Silver Birch", "soil_ph_min": 4.0, "soil_ph_max": 7.0, "drought_tolerant": False, "primary_use": "ornamental", "max_height_m": 25.0, "maintenance_level": "low", "attributes": ["Deciduous", "Fast-growing", "Native"]},
    "Betula pubescens": {"common_name": "Downy Birch", "soil_ph_min": 3.5, "soil_ph_max": 6.5, "drought_tolerant": False, "primary_use": "ornamental", "max_height_m": 20.0, "maintenance_level": "low", "attributes": ["Deciduous", "Native"]},
    "Pinus sylvestris": {"common_name": "Scots Pine", "soil_ph_min": 3.5, "soil_ph_max": 6.5, "drought_tolerant": True, "primary_use": "screening", "max_height_m": 35.0, "maintenance_level": "low", "attributes": ["Evergreen", "Native", "Drought-tolerant"]},
    "Pinus nigra": {"common_name": "Black Pine", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "screening", "max_height_m": 40.0, "maintenance_level": "low", "attributes": ["Evergreen", "Drought-tolerant"]},
    "Pinus pinaster": {"common_name": "Maritime Pine", "soil_ph_min": 4.0, "soil_ph_max": 7.0, "drought_tolerant": True, "primary_use": "screening", "max_height_m": 30.0, "maintenance_level": "low", "attributes": ["Evergreen", "Drought-tolerant"]},
    "Pinus pinea": {"common_name": "Stone Pine", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "shade", "max_height_m": 25.0, "maintenance_level": "low", "attributes": ["Evergreen", "Drought-tolerant"]},
    "Pinus halepensis": {"common_name": "Aleppo Pine", "soil_ph_min": 5.5, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "screening", "max_height_m": 20.0, "maintenance_level": "low", "attributes": ["Evergreen", "Drought-tolerant"]},
    "Pinus mugo": {"common_name": "Mountain Pine", "soil_ph_min": 4.0, "soil_ph_max": 7.5, "drought_tolerant": True, "primary_use": "screening", "max_height_m": 10.0, "maintenance_level": "low", "attributes": ["Evergreen", "Compact"]},
    "Pinus cembra": {"common_name": "Swiss Stone Pine", "soil_ph_min": 4.0, "soil_ph_max": 6.5, "drought_tolerant": False, "primary_use": "ornamental", "max_height_m": 25.0, "maintenance_level": "low", "attributes": ["Evergreen"]},
    "Picea abies": {"common_name": "Norway Spruce", "soil_ph_min": 3.5, "soil_ph_max": 6.0, "drought_tolerant": False, "primary_use": "screening", "max_height_m": 50.0, "maintenance_level": "low", "attributes": ["Evergreen", "Native", "Fast-growing"]},
    "Abies alba": {"common_name": "Silver Fir", "soil_ph_min": 4.0, "soil_ph_max": 7.0, "drought_tolerant": False, "primary_use": "screening", "max_height_m": 50.0, "maintenance_level": "low", "attributes": ["Evergreen", "Native"]},
    "Larix decidua": {"common_name": "European Larch", "soil_ph_min": 4.5, "soil_ph_max": 7.0, "drought_tolerant": False, "primary_use": "ornamental", "max_height_m": 40.0, "maintenance_level": "low", "attributes": ["Deciduous", "Native"]},
    "Acer pseudoplatanus": {"common_name": "Sycamore Maple", "soil_ph_min": 4.5, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "shade", "max_height_m": 30.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Fast-growing"]},
    "Acer platanoides": {"common_name": "Norway Maple", "soil_ph_min": 4.5, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "shade", "max_height_m": 25.0, "maintenance_level": "medium", "attributes": ["Deciduous"]},
    "Acer campestre": {"common_name": "Field Maple", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "ornamental", "max_height_m": 15.0, "maintenance_level": "low", "attributes": ["Deciduous", "Compact", "Native"]},
    "Tilia cordata": {"common_name": "Small-leaved Lime", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": False, "primary_use": "shade", "max_height_m": 30.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Native", "Wildlife-friendly"]},
    "Tilia platyphyllos": {"common_name": "Large-leaved Lime", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": False, "primary_use": "shade", "max_height_m": 35.0, "maintenance_level": "medium", "attributes": ["Deciduous"]},
    "Fraxinus excelsior": {"common_name": "European Ash", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": False, "primary_use": "shade", "max_height_m": 35.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Native", "Fast-growing"]},
    "Fraxinus ornus": {"common_name": "Manna Ash", "soil_ph_min": 5.5, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "ornamental", "max_height_m": 15.0, "maintenance_level": "low", "attributes": ["Deciduous", "Spring blossom"]},
    "Ulmus minor": {"common_name": "Field Elm", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": False, "primary_use": "shade", "max_height_m": 30.0, "maintenance_level": "medium", "attributes": ["Deciduous"]},
    "Ulmus glabra": {"common_name": "Wych Elm", "soil_ph_min": 4.5, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "shade", "max_height_m": 30.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Native"]},
    "Carpinus betulus": {"common_name": "European Hornbeam", "soil_ph_min": 4.5, "soil_ph_max": 8.0, "drought_tolerant": False, "primary_use": "screening", "max_height_m": 25.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Native"]},
    "Castanea sativa": {"common_name": "Sweet Chestnut", "soil_ph_min": 4.5, "soil_ph_max": 6.5, "drought_tolerant": False, "primary_use": "fruit", "max_height_m": 30.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Self-fertile"]},
    "Corylus avellana": {"common_name": "Common Hazel", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": False, "primary_use": "fruit", "max_height_m": 8.0, "maintenance_level": "low", "attributes": ["Deciduous", "Native", "Compact", "Wildlife-friendly"]},
    "Prunus avium": {"common_name": "Wild Cherry", "soil_ph_min": 5.5, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "fruit", "max_height_m": 20.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Self-fertile", "Spring blossom"]},
    "Prunus padus": {"common_name": "Bird Cherry", "soil_ph_min": 5.0, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "wildlife", "max_height_m": 15.0, "maintenance_level": "low", "attributes": ["Deciduous", "Spring blossom", "Wildlife-friendly"]},
    "Prunus spinosa": {"common_name": "Blackthorn", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "wildlife", "max_height_m": 5.0, "maintenance_level": "low", "attributes": ["Deciduous", "Compact", "Wildlife-friendly"]},
    "Malus sylvestris": {"common_name": "European Crab Apple", "soil_ph_min": 5.0, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "fruit", "max_height_m": 10.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Spring blossom", "Wildlife-friendly"]},
    "Pyrus communis": {"common_name": "Common Pear", "soil_ph_min": 5.5, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "fruit", "max_height_m": 15.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Spring blossom"]},
    "Pyrus pyraster": {"common_name": "Wild Pear", "soil_ph_min": 5.5, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "fruit", "max_height_m": 15.0, "maintenance_level": "low", "attributes": ["Deciduous"]},
    "Sorbus aucuparia": {"common_name": "Rowan", "soil_ph_min": 4.0, "soil_ph_max": 7.0, "drought_tolerant": False, "primary_use": "wildlife", "max_height_m": 15.0, "maintenance_level": "low", "attributes": ["Deciduous", "Native", "Wildlife-friendly"]},
    "Sorbus torminalis": {"common_name": "Wild Service Tree", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "wildlife", "max_height_m": 20.0, "maintenance_level": "low", "attributes": ["Deciduous"]},
    "Sorbus domestica": {"common_name": "Service Tree", "soil_ph_min": 5.5, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "fruit", "max_height_m": 18.0, "maintenance_level": "low", "attributes": ["Deciduous"]},
    "Sambucus nigra": {"common_name": "Elder", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": False, "primary_use": "wildlife", "max_height_m": 8.0, "maintenance_level": "low", "attributes": ["Deciduous", "Fast-growing", "Wildlife-friendly", "Compact"]},
    "Populus tremula": {"common_name": "Aspen", "soil_ph_min": 4.0, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "wildlife", "max_height_m": 25.0, "maintenance_level": "low", "attributes": ["Deciduous", "Fast-growing", "Native"]},
    "Populus nigra": {"common_name": "Black Poplar", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": False, "primary_use": "shade", "max_height_m": 30.0, "maintenance_level": "low", "attributes": ["Deciduous", "Fast-growing"]},
    "Populus alba": {"common_name": "White Poplar", "soil_ph_min": 5.0, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "shade", "max_height_m": 25.0, "maintenance_level": "low", "attributes": ["Deciduous", "Fast-growing"]},
    "Salix alba": {"common_name": "White Willow", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": False, "primary_use": "ornamental", "max_height_m": 25.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Fast-growing"]},
    "Salix caprea": {"common_name": "Goat Willow", "soil_ph_min": 4.5, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "wildlife", "max_height_m": 10.0, "maintenance_level": "low", "attributes": ["Deciduous", "Native", "Wildlife-friendly", "Compact"]},
    "Alnus glutinosa": {"common_name": "Common Alder", "soil_ph_min": 4.0, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "wildlife", "max_height_m": 25.0, "maintenance_level": "low", "attributes": ["Deciduous", "Native", "Fast-growing"]},
    "Alnus incana": {"common_name": "Grey Alder", "soil_ph_min": 4.0, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "wildlife", "max_height_m": 20.0, "maintenance_level": "low", "attributes": ["Deciduous", "Fast-growing"]},
    "Taxus baccata": {"common_name": "Common Yew", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "screening", "max_height_m": 20.0, "maintenance_level": "medium", "attributes": ["Evergreen", "Native", "Compact"]},
    "Ilex aquifolium": {"common_name": "Holly", "soil_ph_min": 4.0, "soil_ph_max": 7.0, "drought_tolerant": False, "primary_use": "screening", "max_height_m": 15.0, "maintenance_level": "low", "attributes": ["Evergreen", "Native", "Wildlife-friendly"]},
    "Juglans regia": {"common_name": "Common Walnut", "soil_ph_min": 5.5, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "fruit", "max_height_m": 25.0, "maintenance_level": "medium", "attributes": ["Deciduous"]},
    "Robinia pseudoacacia": {"common_name": "Black Locust", "soil_ph_min": 4.5, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "shade", "max_height_m": 25.0, "maintenance_level": "low", "attributes": ["Deciduous", "Fast-growing", "Drought-tolerant"]},
    "Platanus orientalis": {"common_name": "Oriental Plane", "soil_ph_min": 5.0, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "shade", "max_height_m": 30.0, "maintenance_level": "low", "attributes": ["Deciduous"]},
    "Celtis australis": {"common_name": "European Nettle Tree", "soil_ph_min": 5.5, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "shade", "max_height_m": 25.0, "maintenance_level": "low", "attributes": ["Deciduous", "Drought-tolerant"]},
    "Olea europaea": {"common_name": "Olive", "soil_ph_min": 5.5, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "fruit", "max_height_m": 12.0, "maintenance_level": "low", "attributes": ["Evergreen", "Drought-tolerant"]},
    "Ceratonia siliqua": {"common_name": "Carob", "soil_ph_min": 6.0, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "fruit", "max_height_m": 10.0, "maintenance_level": "low", "attributes": ["Evergreen", "Drought-tolerant", "Compact"]},
    "Arbutus unedo": {"common_name": "Strawberry Tree", "soil_ph_min": 4.5, "soil_ph_max": 7.0, "drought_tolerant": True, "primary_use": "ornamental", "max_height_m": 10.0, "maintenance_level": "low", "attributes": ["Evergreen", "Compact"]},
    "Laurus nobilis": {"common_name": "Bay Laurel", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "ornamental", "max_height_m": 12.0, "maintenance_level": "medium", "attributes": ["Evergreen"]},
    "Cupressus sempervirens": {"common_name": "Italian Cypress", "soil_ph_min": 5.5, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "screening", "max_height_m": 30.0, "maintenance_level": "low", "attributes": ["Evergreen", "Drought-tolerant"]},
    "Juniperus communis": {"common_name": "Common Juniper", "soil_ph_min": 4.0, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "wildlife", "max_height_m": 6.0, "maintenance_level": "low", "attributes": ["Evergreen", "Native", "Compact", "Wildlife-friendly"]},
    "Cedrus atlantica": {"common_name": "Atlas Cedar", "soil_ph_min": 5.0, "soil_ph_max": 7.5, "drought_tolerant": True, "primary_use": "ornamental", "max_height_m": 35.0, "maintenance_level": "low", "attributes": ["Evergreen", "Drought-tolerant"]},
    "Eucalyptus globulus": {"common_name": "Blue Gum", "soil_ph_min": 5.0, "soil_ph_max": 7.5, "drought_tolerant": True, "primary_use": "screening", "max_height_m": 45.0, "maintenance_level": "low", "attributes": ["Evergreen", "Fast-growing"]},
    "Cercis siliquastrum": {"common_name": "Judas Tree", "soil_ph_min": 5.5, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "ornamental", "max_height_m": 10.0, "maintenance_level": "low", "attributes": ["Deciduous", "Spring blossom", "Compact"]},
    "Crataegus monogyna": {"common_name": "Common Hawthorn", "soil_ph_min": 4.5, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "wildlife", "max_height_m": 8.0, "maintenance_level": "low", "attributes": ["Deciduous", "Native", "Compact", "Wildlife-friendly", "Spring blossom"]},
    "Morus alba": {"common_name": "White Mulberry", "soil_ph_min": 5.5, "soil_ph_max": 7.5, "drought_tolerant": True, "primary_use": "fruit", "max_height_m": 15.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Fast-growing"]},
    "Ficus carica": {"common_name": "Common Fig", "soil_ph_min": 5.5, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "fruit", "max_height_m": 8.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Compact"]},
    "Prunus dulcis": {"common_name": "Almond", "soil_ph_min": 5.5, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "fruit", "max_height_m": 8.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Spring blossom"]},
    "Prunus cerasus": {"common_name": "Sour Cherry", "soil_ph_min": 5.5, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "fruit", "max_height_m": 8.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Self-fertile", "Spring blossom", "Compact"]},
    "Prunus domestica": {"common_name": "European Plum", "soil_ph_min": 5.5, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "fruit", "max_height_m": 10.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Self-fertile"]},
    "Malus domestica": {"common_name": "Apple", "soil_ph_min": 5.5, "soil_ph_max": 7.0, "drought_tolerant": False, "primary_use": "fruit", "max_height_m": 10.0, "maintenance_level": "high", "attributes": ["Deciduous", "Spring blossom"]},
    "Pyrus communis subsp. sativa": {"common_name": "Cultivated Pear", "soil_ph_min": 5.5, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "fruit", "max_height_m": 12.0, "maintenance_level": "high", "attributes": ["Deciduous", "Spring blossom"]},
    "Citrus x limon": {"common_name": "Lemon", "soil_ph_min": 5.5, "soil_ph_max": 6.5, "drought_tolerant": False, "primary_use": "fruit", "max_height_m": 6.0, "maintenance_level": "high", "attributes": ["Evergreen", "Compact"]},
    "Citrus x sinensis": {"common_name": "Sweet Orange", "soil_ph_min": 5.5, "soil_ph_max": 6.5, "drought_tolerant": False, "primary_use": "fruit", "max_height_m": 8.0, "maintenance_level": "high", "attributes": ["Evergreen"]},
    "Pistacia lentiscus": {"common_name": "Mastic Tree", "soil_ph_min": 6.0, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "screening", "max_height_m": 5.0, "maintenance_level": "low", "attributes": ["Evergreen", "Compact", "Drought-tolerant"]},
    "Phillyrea latifolia": {"common_name": "Green Olive Tree", "soil_ph_min": 5.5, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "screening", "max_height_m": 8.0, "maintenance_level": "low", "attributes": ["Evergreen", "Drought-tolerant"]},
    "Acer monspessulanum": {"common_name": "Montpellier Maple", "soil_ph_min": 5.5, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "ornamental", "max_height_m": 10.0, "maintenance_level": "low", "attributes": ["Deciduous", "Compact", "Drought-tolerant"]},
    "Abies cephalonica": {"common_name": "Greek Fir", "soil_ph_min": 5.0, "soil_ph_max": 7.5, "drought_tolerant": True, "primary_use": "screening", "max_height_m": 30.0, "maintenance_level": "low", "attributes": ["Evergreen"]},
    "Pinus brutia": {"common_name": "Turkish Pine", "soil_ph_min": 5.5, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "screening", "max_height_m": 25.0, "maintenance_level": "low", "attributes": ["Evergreen", "Drought-tolerant"]},
    "Quercus coccifera": {"common_name": "Kermes Oak", "soil_ph_min": 5.5, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "wildlife", "max_height_m": 6.0, "maintenance_level": "low", "attributes": ["Evergreen", "Compact", "Drought-tolerant"]},
    "Quercus faginea": {"common_name": "Portuguese Oak", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "shade", "max_height_m": 20.0, "maintenance_level": "low", "attributes": ["Deciduous"]},
    "Quercus pyrenaica": {"common_name": "Pyrenean Oak", "soil_ph_min": 4.5, "soil_ph_max": 7.0, "drought_tolerant": False, "primary_use": "shade", "max_height_m": 20.0, "maintenance_level": "low", "attributes": ["Deciduous"]},
    "Quercus rotundifolia": {"common_name": "Holm Oak (Iberian)", "soil_ph_min": 5.0, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "shade", "max_height_m": 20.0, "maintenance_level": "low", "attributes": ["Evergreen", "Drought-tolerant"]},
    "Juniperus oxycedrus": {"common_name": "Prickly Juniper", "soil_ph_min": 5.0, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "wildlife", "max_height_m": 8.0, "maintenance_level": "low", "attributes": ["Evergreen", "Compact", "Drought-tolerant"]},
    "Juniperus thurifera": {"common_name": "Spanish Juniper", "soil_ph_min": 5.5, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "wildlife", "max_height_m": 10.0, "maintenance_level": "low", "attributes": ["Evergreen", "Drought-tolerant"]},
    "Pinus uncinata": {"common_name": "Mountain Pine (Iberian)", "soil_ph_min": 4.0, "soil_ph_max": 7.0, "drought_tolerant": True, "primary_use": "screening", "max_height_m": 20.0, "maintenance_level": "low", "attributes": ["Evergreen"]},
    "Abies nordmanniana": {"common_name": "Nordmann Fir", "soil_ph_min": 5.0, "soil_ph_max": 7.0, "drought_tolerant": False, "primary_use": "ornamental", "max_height_m": 50.0, "maintenance_level": "low", "attributes": ["Evergreen"]},
    "Cedrus libani": {"common_name": "Cedar of Lebanon", "soil_ph_min": 5.0, "soil_ph_max": 7.5, "drought_tolerant": True, "primary_use": "ornamental", "max_height_m": 35.0, "maintenance_level": "low", "attributes": ["Evergreen", "Drought-tolerant"]},
    "Platanus x hispanica": {"common_name": "London Plane", "soil_ph_min": 5.0, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "shade", "max_height_m": 30.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Fast-growing"]},
    "Aesculus hippocastanum": {"common_name": "Horse Chestnut", "soil_ph_min": 5.0, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "shade", "max_height_m": 30.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Spring blossom"]},
    "Gleditsia triacanthos": {"common_name": "Honey Locust", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "shade", "max_height_m": 25.0, "maintenance_level": "low", "attributes": ["Deciduous", "Drought-tolerant"]},
    "Ailanthus altissima": {"common_name": "Tree of Heaven", "soil_ph_min": 4.5, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "shade", "max_height_m": 25.0, "maintenance_level": "low", "attributes": ["Deciduous", "Fast-growing", "Drought-tolerant"]},
    "Liquidambar styraciflua": {"common_name": "Sweetgum", "soil_ph_min": 5.0, "soil_ph_max": 7.0, "drought_tolerant": False, "primary_use": "ornamental", "max_height_m": 30.0, "maintenance_level": "medium", "attributes": ["Deciduous"]},
    "Magnolia grandiflora": {"common_name": "Southern Magnolia", "soil_ph_min": 5.0, "soil_ph_max": 6.5, "drought_tolerant": False, "primary_use": "ornamental", "max_height_m": 25.0, "maintenance_level": "medium", "attributes": ["Evergreen", "Spring blossom"]},
    "Catalpa bignonioides": {"common_name": "Southern Catalpa", "soil_ph_min": 5.5, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "ornamental", "max_height_m": 15.0, "maintenance_level": "low", "attributes": ["Deciduous"]},
    "Paulownia tomentosa": {"common_name": "Empress Tree", "soil_ph_min": 5.0, "soil_ph_max": 7.5, "drought_tolerant": True, "primary_use": "shade", "max_height_m": 15.0, "maintenance_level": "low", "attributes": ["Deciduous", "Fast-growing", "Spring blossom"]},
    "Styphnolobium japonicum": {"common_name": "Japanese Pagoda Tree", "soil_ph_min": 5.5, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "shade", "max_height_m": 20.0, "maintenance_level": "low", "attributes": ["Deciduous"]},
    "Koelreuteria paniculata": {"common_name": "Golden Rain Tree", "soil_ph_min": 5.5, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "ornamental", "max_height_m": 12.0, "maintenance_level": "low", "attributes": ["Deciduous", "Compact"]},
    "Ginkgo biloba": {"common_name": "Ginkgo", "soil_ph_min": 5.0, "soil_ph_max": 7.5, "drought_tolerant": True, "primary_use": "ornamental", "max_height_m": 25.0, "maintenance_level": "low", "attributes": ["Deciduous"]},
    "Mespilus germanica": {"common_name": "Medlar", "soil_ph_min": 5.5, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "fruit", "max_height_m": 6.0, "maintenance_level": "low", "attributes": ["Deciduous", "Compact", "Spring blossom"]},
    "Cydonia oblonga": {"common_name": "Quince", "soil_ph_min": 5.5, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "fruit", "max_height_m": 5.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Compact", "Spring blossom"]},
    "Diospyros kaki": {"common_name": "Persimmon", "soil_ph_min": 5.5, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "fruit", "max_height_m": 10.0, "maintenance_level": "medium", "attributes": ["Deciduous"]},
    "Punica granatum": {"common_name": "Pomegranate", "soil_ph_min": 5.5, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "fruit", "max_height_m": 6.0, "maintenance_level": "medium", "attributes": ["Deciduous", "Compact", "Drought-tolerant"]},
    "Ziziphus jujuba": {"common_name": "Jujube", "soil_ph_min": 5.0, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "fruit", "max_height_m": 8.0, "maintenance_level": "low", "attributes": ["Deciduous", "Drought-tolerant", "Compact"]},
    "Eriobotrya japonica": {"common_name": "Loquat", "soil_ph_min": 5.5, "soil_ph_max": 7.5, "drought_tolerant": True, "primary_use": "fruit", "max_height_m": 8.0, "maintenance_level": "medium", "attributes": ["Evergreen", "Compact"]},
    "Ligustrum lucidum": {"common_name": "Glossy Privet", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "screening", "max_height_m": 12.0, "maintenance_level": "medium", "attributes": ["Evergreen", "Fast-growing"]},
    "Viburnum tinus": {"common_name": "Laurustinus", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "screening", "max_height_m": 4.0, "maintenance_level": "low", "attributes": ["Evergreen", "Compact", "Wildlife-friendly", "Spring blossom"]},
    "Buxus sempervirens": {"common_name": "Common Box", "soil_ph_min": 5.5, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "screening", "max_height_m": 5.0, "maintenance_level": "medium", "attributes": ["Evergreen", "Compact"]},
    "Euonymus europaeus": {"common_name": "European Spindle", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": False, "primary_use": "wildlife", "max_height_m": 6.0, "maintenance_level": "low", "attributes": ["Deciduous", "Native", "Compact", "Wildlife-friendly"]},
    "Rhamnus cathartica": {"common_name": "Common Buckthorn", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "wildlife", "max_height_m": 6.0, "maintenance_level": "low", "attributes": ["Deciduous", "Compact", "Wildlife-friendly"]},
    "Hippophae rhamnoides": {"common_name": "Sea Buckthorn", "soil_ph_min": 5.5, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "wildlife", "max_height_m": 5.0, "maintenance_level": "low", "attributes": ["Deciduous", "Compact", "Drought-tolerant", "Wildlife-friendly"]},
    "Tamarix gallica": {"common_name": "French Tamarisk", "soil_ph_min": 5.5, "soil_ph_max": 9.0, "drought_tolerant": True, "primary_use": "ornamental", "max_height_m": 8.0, "maintenance_level": "low", "attributes": ["Deciduous", "Drought-tolerant"]},
    "Myrtus communis": {"common_name": "Common Myrtle", "soil_ph_min": 5.5, "soil_ph_max": 8.0, "drought_tolerant": True, "primary_use": "ornamental", "max_height_m": 4.0, "maintenance_level": "low", "attributes": ["Evergreen", "Compact"]},
    "Nerium oleander": {"common_name": "Oleander", "soil_ph_min": 5.5, "soil_ph_max": 8.5, "drought_tolerant": True, "primary_use": "screening", "max_height_m": 5.0, "maintenance_level": "medium", "attributes": ["Evergreen", "Compact", "Spring blossom"]},
    "Chamaecyparis lawsoniana": {"common_name": "Lawson Cypress", "soil_ph_min": 5.0, "soil_ph_max": 7.5, "drought_tolerant": False, "primary_use": "screening", "max_height_m": 30.0, "maintenance_level": "medium", "attributes": ["Evergreen"]},
    "Thuja occidentalis": {"common_name": "White Cedar", "soil_ph_min": 5.0, "soil_ph_max": 8.0, "drought_tolerant": False, "primary_use": "screening", "max_height_m": 15.0, "maintenance_level": "medium", "attributes": ["Evergreen"]},
    "Sequoiadendron giganteum": {"common_name": "Giant Sequoia", "soil_ph_min": 5.0, "soil_ph_max": 7.0, "drought_tolerant": False, "primary_use": "ornamental", "max_height_m": 60.0, "maintenance_level": "low", "attributes": ["Evergreen"]},
    "Metasequoia glyptostroboides": {"common_name": "Dawn Redwood", "soil_ph_min": 5.0, "soil_ph_max": 7.0, "drought_tolerant": False, "primary_use": "ornamental", "max_height_m": 35.0, "maintenance_level": "low", "attributes": ["Deciduous", "Fast-growing"]},
    "Cryptomeria japonica": {"common_name": "Japanese Cedar", "soil_ph_min": 5.0, "soil_ph_max": 6.5, "drought_tolerant": False, "primary_use": "screening", "max_height_m": 40.0, "maintenance_level": "low", "attributes": ["Evergreen"]},
}

WIKIMEDIA_BASE = "https://commons.wikimedia.org/wiki/Special:FilePath"

# Wikimedia Commons image filenames for species
IMAGE_FILES: dict[str, str] = {
    "Quercus robur": "Quercus_robur_JPG_(d1).jpg",
    "Fagus sylvatica": "Fagus_sylvatica_JPG1a.jpg",
    "Betula pendula": "Betula_pendula_001.jpg",
    "Pinus sylvestris": "Pinus_sylvestris_Aland.jpg",
    "Picea abies": "Picea_abies.jpg",
    "Prunus avium": "Prunus_avium_fruit.jpg",
    "Olea europaea": "Olea_europaea_subsp._europaea_(wild).jpg",
    "Castanea sativa": "Castanea_sativa_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-172.jpg",
    "Acer pseudoplatanus": "Acer_pseudoplatanus_004.jpg",
    "Tilia cordata": "Tilia_cordata_015.jpg",
}


def get_image_url(scientific_name: str) -> str:
    """Get Wikimedia Commons image URL for a species."""
    filename = IMAGE_FILES.get(scientific_name, "")
    if filename:
        return f"{WIKIMEDIA_BASE}/{filename}"
    return ""


def merge_layers(
    eu_forest_data: list[dict[str, object]],
    med_db_data: list[dict[str, object]],
    eu_trees4f_data: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Merge EU-Forest (primary), Med DB (enrichment), EU-Trees4F (validation) into unified species list."""
    # Index supplementary data by scientific_name
    med_index: dict[str, dict[str, object]] = {
        str(entry["scientific_name"]): entry for entry in med_db_data
    }
    trees4f_species: set[str] = {
        str(entry["scientific_name"]) for entry in eu_trees4f_data
    }
    unified: list[dict[str, object]] = []
    seen_species: set[str] = set()

    # Layer 1: EU-Forest as primary (species + climate zones)
    for entry in eu_forest_data:
        sci_name = str(entry["scientific_name"])
        if sci_name in seen_species:
            continue
        seen_species.add(sci_name)

        defaults = SPECIES_DEFAULTS.get(sci_name, {})

        species_record: dict[str, object] = {
            "scientific_name": sci_name,
            "common_name": defaults.get("common_name", sci_name),
            "koppen_zones": entry.get("koppen_zones", []),
            "soil_ph_min": defaults.get("soil_ph_min", 5.0),
            "soil_ph_max": defaults.get("soil_ph_max", 7.5),
            "drought_tolerant": defaults.get("drought_tolerant", False),
            "primary_use": defaults.get("primary_use", "ornamental"),
            "max_height_m": defaults.get("max_height_m", 15.0),
            "maintenance_level": defaults.get("maintenance_level", "medium"),
            "image_url": get_image_url(sci_name),
            "attributes": defaults.get("attributes", []),
        }

        # Layer 2: Med DB enrichment (habitat/use for Mediterranean species)
        med_entry = med_index.get(sci_name)
        if med_entry:
            if "primary_use" in med_entry:
                species_record["primary_use"] = med_entry["primary_use"]

        unified.append(species_record)

    # Add species from defaults that weren't in EU-Forest (cultivated/urban species)
    for sci_name, defaults in SPECIES_DEFAULTS.items():
        if sci_name in seen_species:
            continue
        seen_species.add(sci_name)

        # Assign basic climate zones based on species type
        koppen_zones = _infer_climate_zones(sci_name, defaults)

        species_record = {
            "scientific_name": sci_name,
            "common_name": defaults.get("common_name", sci_name),
            "koppen_zones": koppen_zones,
            "soil_ph_min": defaults.get("soil_ph_min", 5.0),
            "soil_ph_max": defaults.get("soil_ph_max", 7.5),
            "drought_tolerant": defaults.get("drought_tolerant", False),
            "primary_use": defaults.get("primary_use", "ornamental"),
            "max_height_m": defaults.get("max_height_m", 15.0),
            "maintenance_level": defaults.get("maintenance_level", "medium"),
            "image_url": get_image_url(sci_name),
            "attributes": defaults.get("attributes", []),
        }
        unified.append(species_record)

    # Layer 3: EU-Trees4F distribution validation
    validated_count = sum(1 for r in unified if str(r["scientific_name"]) in trees4f_species)
    print(f"Merged {len(unified)} species into unified database.")
    if trees4f_species:
        print(f"EU-Trees4F validation: {validated_count}/{len(unified)} species confirmed in distribution data.")
    return unified


def _infer_climate_zones(scientific_name: str, defaults: dict[str, object]) -> list[str]:
    """Infer likely Köppen zones for species not in EU-Forest dataset."""
    drought_tolerant = defaults.get("drought_tolerant", False)
    if drought_tolerant:
        return ["Csa", "Csb", "Cfa", "Cfb"]
    return ["Cfb", "Cfa", "Dfb"]


def build_tree_database(
    eu_forest_csv: Path | None = None,
    med_db_csv: Path | None = None,
    eu_trees4f_csv: Path | None = None,
) -> list[dict[str, object]]:
    """Build the unified tree species database from all sources."""
    from scripts.etl.process_eu_forest import process_eu_forest
    from scripts.etl.process_eu_trees4f import process_eu_trees4f
    from scripts.etl.process_med_db import process_med_db

    eu_forest_data: list[dict[str, object]] = []
    if eu_forest_csv and eu_forest_csv.exists():
        eu_forest_data = process_eu_forest(eu_forest_csv)
    else:
        print("No EU-Forest CSV provided, using defaults only.")

    med_db_data: list[dict[str, object]] = []
    if med_db_csv and med_db_csv.exists():
        med_db_data = process_med_db(med_db_csv)

    eu_trees4f_data: list[dict[str, object]] = []
    if eu_trees4f_csv and eu_trees4f_csv.exists():
        eu_trees4f_data = process_eu_trees4f(eu_trees4f_csv)

    unified = merge_layers(eu_forest_data, med_db_data, eu_trees4f_data)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DIR / "tree_species.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(unified, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(unified)} species to {output_path}")

    return unified


if __name__ == "__main__":
    raw_dir = RAW_DIR
    eu_forest_csv = raw_dir / "EUForestspecies.csv"
    med_db_csv = raw_dir / "med_species.csv"
    eu_trees4f_csv = raw_dir / "eu_trees4f_species.csv"

    build_tree_database(
        eu_forest_csv=eu_forest_csv if eu_forest_csv.exists() else None,
        med_db_csv=med_db_csv if med_db_csv.exists() else None,
        eu_trees4f_csv=eu_trees4f_csv if eu_trees4f_csv.exists() else None,
    )
