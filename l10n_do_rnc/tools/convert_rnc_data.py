#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para convertir archivo TXT de RNC a formato JSON comprimido
Uso: python3 convert_rnc_data.py input_file.txt output_directory
"""

import json
import gzip
import os
import sys
import argparse
from datetime import datetime
import chardet

def detect_encoding(file_path):
    """
    Detects the encoding of the file
    """
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']
        
        print(f"Encoding detected: {encoding} (confidence: {confidence:.2%})")
        
        # If the confidence is low, try common encodings
        if confidence < 0.7:
            common_encodings = ['latin-1', 'cp1252', 'iso-8859-1', 'utf-8']
            for enc in common_encodings:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        f.read(1000)  # Try reading
                    print(f"Valid encoding found: {enc}")
                    return enc
                except UnicodeDecodeError:
                    continue
        
        return encoding

def convert_txt_to_json_gz(txt_file_path, output_dir):
    """
    Converts TXT file of RNC to compressed JSON
    
    Args:
        txt_file_path (str): Ruta al archivo TXT de entrada
        output_dir (str): Directorio de salida para el archivo JSON.gz
    """
    data = []
    processed = 0
    errors = 0
    
    print(f"Procesando archivo: {txt_file_path}")
    
    try:
        # Detectar codificación
        encoding = detect_encoding(txt_file_path)
        
        with open(txt_file_path, 'r', encoding=encoding) as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split('|')
                if len(parts) >= 2:
                    rnc = parts[0].strip()
                    name = parts[1].strip()
                    
                    # Validate that RNC has 9 or 11 digits (RNC or cedula)
                    if rnc.isdigit() and len(rnc) in [9, 11]:
                        data.append({
                            'rnc': rnc,
                            'name': name
                        })
                        processed += 1
                    else:
                        errors += 1
                        if errors <= 10:  # Show only the first 10 errors
                            print(f"  Error line {line_num}: Invalid RNC '{rnc}' (length: {len(rnc)})")
                else:
                    errors += 1
                    if errors <= 10:
                        print(f"  Error line {line_num}: Invalid format")
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save as compressed JSON
        output_path = os.path.join(output_dir, 'rnc_data.json.gz')
        with gzip.open(output_path, 'wt', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Estadísticas
        file_size = os.path.getsize(output_path)
        file_size_mb = file_size / 1024 / 1024
        
        print(f"\nConversion completed:")
        print(f"  Processed records: {processed:,}")
        print(f"  Found errors: {errors}")
        print(f"  Generated file: {output_path}")
        print(f"  Size: {file_size_mb:.2f} MB")
        print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except FileNotFoundError:
        print(f"Error: File not found: {txt_file_path}")
        return False
    except UnicodeDecodeError as e:
        print(f"Error of encoding: {e}")
        print("Trying with alternative encodings...")
        
        # Try with alternative encodings
        alternative_encodings = ['latin-1', 'cp1252', 'iso-8859-1']
        for alt_encoding in alternative_encodings:
            try:
                print(f"Testing encoding: {alt_encoding}")
                return convert_with_encoding(txt_file_path, output_dir, alt_encoding)
            except UnicodeDecodeError:
                continue
        
        print("No valid encoding found")
        return False
    except Exception as e:
        print(f"Error processing file: {e}")
        return False

def convert_with_encoding(txt_file_path, output_dir, encoding):
    """
    Converts file with a specific encoding
    """
    data = []
    processed = 0
    errors = 0
    
    print(f"Processing with encoding: {encoding}")
    
    with open(txt_file_path, 'r', encoding=encoding) as file:
        for line_num, line in enumerate(file, 1):
            line = line.strip()
            if not line:
                continue
                
            parts = line.split('|')
            if len(parts) >= 2:
                rnc = parts[0].strip()
                name = parts[1].strip()
                
                # Validate that RNC has 9 or 11 digits (RNC or cedula)
                if rnc.isdigit() and len(rnc) in [9, 11]:
                    data.append({
                        'rnc': rnc,
                        'name': name
                    })
                    processed += 1
                else:
                    errors += 1
                    if errors <= 10:
                        print(f"  Error line {line_num}: Invalid RNC '{rnc}' (length: {len(rnc)})")
            else:
                errors += 1
                if errors <= 10:
                    print(f"  Error line {line_num}: Invalid format")
    
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as compressed JSON
    output_path = os.path.join(output_dir, 'rnc_data.json.gz')
    with gzip.open(output_path, 'wt', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Estadísticas
    file_size = os.path.getsize(output_path)
    file_size_mb = file_size / 1024 / 1024
    
    print(f"\nConversion completed with {encoding}:")
    print(f"  Processed records: {processed:,}")
    print(f"  Found errors: {errors}")
    print(f"  Generated file: {output_path}")
    print(f"  Size: {file_size_mb:.2f} MB")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

def main():
    """Main function of the script"""
    parser = argparse.ArgumentParser(
        description='Converts TXT file of RNC to compressed JSON'
    )
    parser.add_argument(
        'input_file',
        help='Path to the input TXT file'
    )
    parser.add_argument(
        'output_dir',
        help='Output directory for the JSON.gz file'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}")
        sys.exit(1)
    
    success = convert_txt_to_json_gz(args.input_file, args.output_dir)
    
    if success:
        print("\nProcess completed successfully!")
        sys.exit(0)
    else:
        print("\nProcess failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 