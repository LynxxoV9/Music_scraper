#!/usr/bin/env python3
"""
Script de téléchargement de musiques par artiste
Version simplifiée et fonctionnelle
"""

import os
import sys
from pathlib import Path
import yt_dlp

class MusicDownloader:
    def __init__(self):
        self.selected_tracks = set()
        self.base_music_dir = Path.home() / "Music"
        self.base_music_dir.mkdir(exist_ok=True)
    
    def search_artist_songs(self, artist_name, limit):
        """Recherche les chansons d'un artiste"""
        print(f"\nRecherche des musiques de : {artist_name}\n")
        
        songs = []
        
        try:
            # Configuration yt-dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Recherche YouTube
                search_query = f"ytsearch{limit}:{artist_name}"
                print(f"Recherche en cours...")
                
                info = ydl.extract_info(search_query, download=False)
                
                if not info or 'entries' not in info:
                    return [], artist_name
                
                # Parcourir les résultats
                for idx, entry in enumerate(info['entries']):
                    if entry is None:
                        continue
                    
                    # Récupérer la durée
                    duration = entry.get('duration', 0)
                    
                    # Filtrer : entre 30 secondes et 15 minutes
                    if duration and 30 < duration < 900:
                        minutes = duration // 60
                        seconds = duration % 60
                        
                        songs.append({
                            'index': idx,
                            'title': entry.get('title', 'Sans titre'),
                            'artist': entry.get('uploader', artist_name),
                            'duration': f"{minutes}:{seconds:02d}",
                            'url': entry.get('webpage_url', ''),
                            'id': entry.get('id', ''),
                        })
                    
                    if len(songs) >= limit:
                        break
                
                print(f"Trouvé {len(songs)} chanson(s)\n")
                
        except Exception as e:
            print(f"Erreur : {e}\n")
            return [], artist_name
        
        # Déterminer le nom réel de l'artiste
        artist_real = artist_name
        for song in songs:
            if 'Topic' in song['artist'] or 'VEVO' in song['artist']:
                artist_real = song['artist'].replace(' - Topic', '').replace('VEVO', '').strip()
                break
        
        return songs, artist_real
    
    def display_songs(self, songs):
        """Affiche la liste des chansons"""
        print(f"\n{'#':<4} {'[X]':<5} {'Titre':<50} {'Durée':<8}")
        print("=" * 70)
        
        for song in songs:
            sel = '[X]' if song['index'] in self.selected_tracks else '[ ]'
            title = song['title'][:48] + '..' if len(song['title']) > 50 else song['title']
            print(f"{song['index']:<4} {sel:<5} {title:<50} {song['duration']:<8}")
    
    def select_all(self, songs):
        """Sélectionner tout"""
        self.selected_tracks = {s['index'] for s in songs}
    
    def deselect_all(self):
        """Désélectionner tout"""
        self.selected_tracks.clear()
    
    def toggle_selection(self, idx):
        """Inverser la sélection"""
        if idx in self.selected_tracks:
            self.selected_tracks.remove(idx)
        else:
            self.selected_tracks.add(idx)
    
    def download_songs(self, songs, output_dir):
        """Télécharger les chansons sélectionnées"""
        if not self.selected_tracks:
            print("\nAucune chanson sélectionnée.\n")
            return
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        selected = [s for s in songs if s['index'] in self.selected_tracks]
        total = len(selected)
        
        print(f"\nTéléchargement de {total} chanson(s) dans : {output_dir}\n")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'quiet': False,
            'no_warnings': False,
        }
        
        success = 0
        failed = 0
        
        for i, song in enumerate(selected, 1):
            try:
                print(f"\n[{i}/{total}] {song['title']}")
                print("=" * 70)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([song['url']])
                
                success += 1
                print("\nRéussi !")
                
            except Exception as e:
                failed += 1
                print(f"\nErreur : {e}")
        
        print(f"\n{'='*70}")
        print(f"Réussis : {success}/{total}")
        print(f"Échecs  : {failed}/{total}")
        print(f"Dossier : {output_dir}")
        print(f"{'='*70}\n")
    
    def menu(self, songs, output_dir):
        """Menu interactif"""
        while True:
            os.system('clear')
            
            print("\n" + "="*70)
            print("TÉLÉCHARGEUR DE MUSIQUES".center(70))
            print("="*70)
            
            self.display_songs(songs)
            
            print(f"\nSélectionnées : {len(self.selected_tracks)}/{len(songs)}")
            print(f"Destination   : {output_dir}")
            
            print("\n" + "-"*70)
            print("OPTIONS :")
            print("  [Numéro] - Sélectionner/désélectionner")
            print("  [a]      - Tout sélectionner")
            print("  [d]      - Tout désélectionner")
            print("  [t]      - Télécharger")
            print("  [q]      - Quitter")
            print("-"*70)
            
            choice = input("\nChoix : ").strip().lower()
            
            if choice == 'q':
                sys.exit(0)
            elif choice == 'a':
                self.select_all(songs)
            elif choice == 'd':
                self.deselect_all()
            elif choice == 't':
                os.system('clear')
                self.download_songs(songs, output_dir)
                input("\nAppuyez sur Entrée...")
            elif choice.isdigit():
                idx = int(choice)
                if 0 <= idx < len(songs):
                    self.toggle_selection(idx)
    
    def run(self):
        """Lancer l'application"""
        os.system('clear')
        
        print("\n" + "="*70)
        print("TÉLÉCHARGEUR DE MUSIQUES".center(70))
        print("="*70 + "\n")
        
        artist_name = input("Nom de l'artiste : ").strip()
        if not artist_name:
            print("Nom invalide.")
            sys.exit(1)
        
        try:
            limit = int(input("Nombre de musiques (défaut 30) : ") or "30")
            limit = max(1, min(limit, 100))
        except:
            limit = 30
        
        songs, artist_real = self.search_artist_songs(artist_name, limit)
        
        if not songs:
            print("\nAucune musique trouvée.")
            print("Vérifiez le nom de l'artiste.\n")
            sys.exit(1)
        
        print(f"{len(songs)} chanson(s) trouvée(s) !")
        input("\nAppuyez sur Entrée...")
        
        artist_dir = self.base_music_dir / artist_real
        self.menu(songs, artist_dir)

if __name__ == "__main__":
    try:
        MusicDownloader().run()
    except KeyboardInterrupt:
        print("\n\nInterrompu.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\nErreur : {e}\n")
        sys.exit(1)
