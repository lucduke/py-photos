#!/usr/bin/env python3
"""
Module pour gérer les différentes commandes du programme de reconnaissance de numéros de voitures
"""

import logging
from pathlib import Path
from .models import Config, CarNumberRecognizer, ImageHashCalculator
import xml.etree.ElementTree as ET


def run_car_recognition(config: Config) -> None:
    """
    Exécute la reconnaissance des numéros de voitures
    
    Args:
        config: Configuration du script
    """
    try:
        # Initialisation du recognizer
        recognizer = CarNumberRecognizer(config)
        
        # Traitement des images
        logging.info(f"Début du traitement des images dans: {config.photos_folder}")
        recognizer.process_images()
        
        # Génération du résumé
        recognizer.generate_summary()
        
        # Nettoyage des fichiers temporaires si nécessaire
        recognizer.cleanup_converted_files()
        
        # Utiliser le nom du fichier généré si disponible
        output_file_path = getattr(recognizer, 'output_file_path', config.output_file)
        logging.info(f"Résultats sauvegardés dans: {output_file_path}")
        
    except Exception as e:
        logging.error(f"Erreur lors de la reconnaissance des numéros de voitures: {e}")
        raise


def run_move_photos(config: Config) -> None:
    """
    Déplace les photos dans des sous-répertoires selon le numéro de voiture
    
    Args:
        config: Configuration du script
    """
    try:
        # Lecture du fichier de résultats
        results_file = Path(config.output_file)
        if not results_file.exists():
            logging.error(f"Le fichier de résultats {results_file} n'existe pas")
            return
        
        # Création d'un dictionnaire pour stocker les numéros de voiture et les fichiers associés
        car_files = {}
        
        with open(results_file, 'r', encoding='utf-8') as f:
            # Sauter l'en-tête
            next(f)
            
            for line in f:
                parts = line.strip().split(';')
                if len(parts) == 2:
                    filename, car_number = parts
                    if car_number not in ['ERROR', 'NONE']:
                        if car_number not in car_files:
                            car_files[car_number] = []
                        car_files[car_number].append(filename)
        
        # Déplacement des fichiers
        photos_path = Path(config.photos_folder)
        for car_number, files in car_files.items():
            # Création du sous-répertoire pour ce numéro de voiture
            car_folder = photos_path / f"car_{car_number}"
            car_folder.mkdir(exist_ok=True)
            
            # Déplacement des fichiers
            for filename in files:
                source_file = photos_path / filename
                destination_file = car_folder / filename
                
                if source_file.exists():
                    try:
                        source_file.rename(destination_file)
                        logging.info(f"Déplacé {filename} vers {car_folder}")
                    except Exception as e:
                        logging.error(f"Erreur lors du déplacement de {filename}: {e}")
                else:
                    logging.warning(f"Fichier {filename} non trouvé")
        
        logging.info("Déplacement des photos terminé")
        
    except Exception as e:
        logging.error(f"Erreur lors du déplacement des photos: {e}")
        raise

def run_update_xmp(config: Config) -> None:
    """
    Met à jour les métadonnées XMP des photos

    Args:
        config: Configuration du script
    """
    try:
        # Lecture des fichiers XMP
        xmp_folder = Path(config.xmp_folder)
        if not xmp_folder.exists():
            logging.error(f"Le dossier XMP {xmp_folder} n'existe pas")
            return

        # Traitement des fichiers XMP
        logging.info(f"Début de la mise à jour des métadonnées XMP dans: {xmp_folder}") 

        for xmp_file in xmp_folder.glob("*.xmp"):
            logging.info(f"Traitement du fichier XMP: {xmp_file.name}")
            
            # Mise à jour des balises XMP spécifiques avec des données prédéfinies
            logging.info(f"Mise à jour du fichier XMP {xmp_file.name} avec les données prédéfinies")
            
            try:
                # Lecture du fichier XMP
                with open(xmp_file, 'r', encoding='utf-8') as f:
                    xmp_content = f.read()
                
                # Ajout des espaces de noms pour le parsing XML
                namespaces = {
                    'x': 'adobe:ns:meta/',
                    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                    'photoshop': 'http://ns.adobe.com/photoshop/1.0/',
                    'dc': 'http://purl.org/dc/elements/1.1/',
                    'Iptc4xmpCore': 'http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/',
                    'xmpRights': 'http://ns.adobe.com/xap/1.0/rights/',
                    'plus_1_': 'http://ns.useplus.org/ldf/xmp/1.0/ImageCreator'
                }
                
                # Enregistrement des espaces de noms
                for prefix, uri in namespaces.items():
                    ET.register_namespace(prefix, uri)
                
                # Parsing du contenu XMP
                root = ET.fromstring(xmp_content)
                
                # Recherche de la balise rdf:Description
                rdf_description = root.find(".//rdf:Description", namespaces)
                
                if rdf_description is not None:
                    # Mise à jour des balises XMP avec des données prédéfinies
                    # photoshop:City
                    city_value = "Tashkent"
                    rdf_description.set(f"{{{namespaces['photoshop']}}}City", city_value)
                    # photoshop:Country
                    country_value = "Ouzbékistan"
                    rdf_description.set(f"{{{namespaces['photoshop']}}}Country", country_value)
                    # photoshop:Headline
                    headline_value = "Vacances 2025 Ouzbékistan"
                    rdf_description.set(f"{{{namespaces['photoshop']}}}Headline", headline_value)
                    
                    # dc:rights - mise à jour de la valeur dans rdf:li
                    rights_element = rdf_description.find(f"{{{namespaces['dc']}}}rights/{{{namespaces['rdf']}}}Alt/{{{namespaces['rdf']}}}li")
                    rights_value = "© 2025 - Tous droits réservés - Christophe Genestet"
                    if rights_element is not None:
                        rights_element.text = rights_value
                    else:
                        # Si la structure n'existe pas, on la crée
                        rights_element = ET.SubElement(rdf_description, f"{{{namespaces['dc']}}}rights")
                        alt_element = ET.SubElement(rights_element, f"{{{namespaces['rdf']}}}Alt")
                        li_element = ET.SubElement(alt_element, f"{{{namespaces['rdf']}}}li")
                        li_element.set("xml:lang", "x-default")
                        li_element.text = rights_value

                    # dc:creator - mise à jour de la valeur dans rdf:li
                    creator_element = rdf_description.find(f"{{{namespaces['dc']}}}creator/{{{namespaces['rdf']}}}Seq/{{{namespaces['rdf']}}}li")
                    creator_value = "Christophe GENESTET"
                    if creator_element is not None:
                        creator_element.text = creator_value
                    else:
                        # Si la structure n'existe pas, on la crée
                        creator_element = ET.SubElement(rdf_description, f"{{{namespaces['dc']}}}creator")
                        seq_element = ET.SubElement(creator_element, f"{{{namespaces['rdf']}}}Seq")
                        li_element = ET.SubElement(seq_element, f"{{{namespaces['rdf']}}}li")
                        li_element.text = creator_value
                    
                    # dc:description - mise à jour de la valeur dans rdf:li
                    description_element = rdf_description.find(f"{{{namespaces['dc']}}}description/{{{namespaces['rdf']}}}Alt/{{{namespaces['rdf']}}}li")
                    description_value = config.xmp_dc_description
                    if description_element is not None:
                        description_element.text = description_value
                    else:
                        # Si la structure n'existe pas, on la crée
                        description_element = ET.SubElement(rdf_description, f"{{{namespaces['dc']}}}description")
                        alt_element = ET.SubElement(description_element, f"{{{namespaces['rdf']}}}Alt")
                        li_element = ET.SubElement(alt_element, f"{{{namespaces['rdf']}}}li")
                        li_element.set("xml:lang", "x-default")
                        li_element.text = description_value
                    
                    # Iptc4xmpCore:CountryCode
                    country_code_value = "FR"
                    rdf_description.set(f"{{{namespaces['Iptc4xmpCore']}}}CountryCode", country_code_value)
                    
                    # Iptc4xmpCore:CiAdrCity - mise à jour dans Iptc4xmpCore:CreatorContactInfo
                    creator_contact_info = rdf_description.find(f"{{{namespaces['Iptc4xmpCore']}}}CreatorContactInfo")
                    city_value = "Puteaux"
                    if creator_contact_info is not None:
                        city_element = creator_contact_info.find(f"{{{namespaces['Iptc4xmpCore']}}}CiAdrCity")
                        if city_element is not None:
                            city_element.text = city_value
                        else:
                            city_element = ET.SubElement(creator_contact_info, f"{{{namespaces['Iptc4xmpCore']}}}CiAdrCity")
                            city_element.text = city_value
                    else:
                        # Si la structure n'existe pas, on la crée
                        creator_contact_info = ET.SubElement(rdf_description, f"{{{namespaces['Iptc4xmpCore']}}}CreatorContactInfo")
                        creator_contact_info.set("rdf:parseType", "Resource")
                        city_element = ET.SubElement(creator_contact_info, f"{{{namespaces['Iptc4xmpCore']}}}CiAdrCity")
                        city_element.text = city_value

                    # Iptc4xmpCore:CiAdrCtry - mise à jour dans Iptc4xmpCore:CreatorContactInfo
                    creator_contact_info = rdf_description.find(f"{{{namespaces['Iptc4xmpCore']}}}CreatorContactInfo")
                    country_value = "France"
                    if creator_contact_info is not None:
                        country_element = creator_contact_info.find(f"{{{namespaces['Iptc4xmpCore']}}}CiAdrCtry")
                        if country_element is not None:
                            country_element.text = country_value
                        else:
                            country_element = ET.SubElement(creator_contact_info, f"{{{namespaces['Iptc4xmpCore']}}}CiAdrCtry")
                            country_element.text = country_value
                    else:
                        # Si la structure n'existe pas, on la crée
                        creator_contact_info = ET.SubElement(rdf_description, f"{{{namespaces['Iptc4xmpCore']}}}CreatorContactInfo")
                        creator_contact_info.set("rdf:parseType", "Resource")
                        country_element = ET.SubElement(creator_contact_info, f"{{{namespaces['Iptc4xmpCore']}}}CiAdrCtry")
                        country_element.text = country_value
                    
                    # Iptc4xmpCore:CiEmailWork - mise à jour dans Iptc4xmpCore:CreatorContactInfo
                    creator_contact_info = rdf_description.find(f"{{{namespaces['Iptc4xmpCore']}}}CreatorContactInfo")
                    email_value = "christophe.genestet@gmail.com"
                    if creator_contact_info is not None:
                        email_element = creator_contact_info.find(f"{{{namespaces['Iptc4xmpCore']}}}CiEmailWork")
                        if email_element is not None:
                            email_element.text = email_value
                        else:
                            email_element = ET.SubElement(creator_contact_info, f"{{{namespaces['Iptc4xmpCore']}}}CiEmailWork")
                            email_element.text = email_value
                    else:
                        # Si la structure n'existe pas, on la crée
                        creator_contact_info = ET.SubElement(rdf_description, f"{{{namespaces['Iptc4xmpCore']}}}CreatorContactInfo")
                        creator_contact_info.set("rdf:parseType", "Resource")
                        email_element = ET.SubElement(creator_contact_info, f"{{{namespaces['Iptc4xmpCore']}}}CiEmailWork")
                        email_element.text = email_value

                    # Iptc4xmpCore:CiAdrPcode - mise à jour dans Iptc4xmpCore:CreatorContactInfo
                    creator_contact_info = rdf_description.find(f"{{{namespaces['Iptc4xmpCore']}}}CreatorContactInfo")
                    pcode_value = "92800"
                    if creator_contact_info is not None:
                        pcode_element = creator_contact_info.find(f"{{{namespaces['Iptc4xmpCore']}}}CiAdrPcode")
                        if pcode_element is not None:
                            pcode_element.text = pcode_value
                        else:
                            pcode_element = ET.SubElement(creator_contact_info, f"{{{namespaces['Iptc4xmpCore']}}}CiAdrPcode")
                            pcode_element.text = pcode_value
                    else:
                        # Si la structure n'existe pas, on la crée
                        creator_contact_info = ET.SubElement(rdf_description, f"{{{namespaces['Iptc4xmpCore']}}}CreatorContactInfo")
                        creator_contact_info.set("rdf:parseType", "Resource")
                        pcode_element = ET.SubElement(creator_contact_info, f"{{{namespaces['Iptc4xmpCore']}}}CiAdrPcode")
                        pcode_element.text = pcode_value

                    # xmpRights:UsageTerms - mise à jour de la valeur dans rdf:li
                    usage_terms_element = rdf_description.find(f"{{{namespaces['xmpRights']}}}UsageTerms/{{{namespaces['rdf']}}}Alt/{{{namespaces['rdf']}}}li")
                    usage_terms_value = "Interdiction de copier et diffuser cette image sans accord ecrit de l'auteur"
                    if usage_terms_element is not None:
                        usage_terms_element.text = usage_terms_value
                    else:
                        # Si la structure n'existe pas, on la crée
                        usage_terms_element = ET.SubElement(rdf_description, f"{{{namespaces['xmpRights']}}}UsageTerms")
                        alt_element = ET.SubElement(usage_terms_element, f"{{{namespaces['rdf']}}}Alt")
                        li_element = ET.SubElement(alt_element, f"{{{namespaces['rdf']}}}li")
                        li_element.set("xml:lang", "x-default")
                        li_element.text = usage_terms_value

                    # plus_1_:ImageCreator - mise à jour de la valeur dans plus_1_:ImageCreatorName
                    image_creator_element = rdf_description.find(f"{{{namespaces['plus_1_']}}}ImageCreator")

                    if image_creator_element is not None:
                        # Recherche de l'élément plus_1_:ImageCreatorName
                        seq_element = image_creator_element.find(f"{{{namespaces['rdf']}}}Seq")
                        if seq_element is not None:
                            li_element = seq_element.find(f"{{{namespaces['rdf']}}}li")
                            if li_element is not None:
                                resource_element = li_element.find(f"{{{namespaces['plus_1_']}}}ImageCreatorName")
                                if resource_element is not None:
                                    resource_element.text = creator_value
                                else:
                                    # Si la structure n'existe pas, on la crée
                                    resource_element = ET.SubElement(li_element, f"{{{namespaces['plus_1_']}}}ImageCreatorName")
                                    resource_element.text = creator_value
                            else:
                                # Si la structure n'existe pas, on la crée
                                li_element = ET.SubElement(seq_element, f"{{{namespaces['rdf']}}}li")
                                li_element.set("rdf:parseType", "Resource")
                                resource_element = ET.SubElement(li_element, f"{{{namespaces['plus_1_']}}}ImageCreatorName")
                                resource_element.text = creator_value
                    else:
                        # Si la structure n'existe pas, on la crée
                        image_creator_element = ET.SubElement(rdf_description, f"{{{namespaces['plus_1_']}}}ImageCreator")
                        seq_element = ET.SubElement(image_creator_element, f"{{{namespaces['rdf']}}}Seq")
                        li_element = ET.SubElement(seq_element, f"{{{namespaces['rdf']}}}li")
                        li_element.set("rdf:parseType", "Resource")
                        resource_element = ET.SubElement(li_element, f"{{{namespaces['plus_1_']}}}ImageCreatorName")
                        resource_element.text = creator_value

                    # Conversion de l'arbre XML en chaîne de caractères
                    new_xmp_content = ET.tostring(root, encoding='unicode')
                    
                    # Écriture du fichier XMP mis à jour
                    with open(xmp_file, 'w', encoding='utf-8') as f:
                        f.write(new_xmp_content)
                    
                    logging.info(f"Fichier XMP {xmp_file.name} mis à jour avec les données prédéfinies")
                else:
                    logging.error(f"Impossible de trouver la balise rdf:Description dans le fichier XMP {xmp_file.name}")
                
            except Exception as e:
                logging.error(f"Erreur lors de la mise à jour du fichier XMP {xmp_file.name}: {e}")
                continue

    except Exception as e:
        logging.error(f"Erreur lors de la mise à jour des métadonnées XMP: {e}")
        raise

def run_calculate_hash(config: Config) -> None:
    """
    Calcule le hash des fichiers photo à partir de la librairie imagehash (fonctionnalité à implémenter)

    Args:
        config: Configuration du script
    """
    try:
        logging.info("Calcul du hash des fichiers photo")
        hash_calculator = ImageHashCalculator(config)
        hash_calculator.calculate_hashes()

    except Exception as e:
        logging.error(f"Erreur lors du calcul du hash des fichiers photo: {e}")
        raise