"""
Sound Alert Player
Plays audio alerts for different probability levels
"""

import logging
from typing import Dict, List
from pathlib import Path

try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logging.warning("pygame not installed - sound alerts disabled")

logger = logging.getLogger(__name__)


class SoundPlayer:
    """Play sound alerts"""
    
    def __init__(self, config: Dict):
        """
        Initialize sound player
        
        Args:
            config: Configuration dictionary
        """
        self.enabled = config.get('SOUND_ALERTS_ENABLED', False) and PYGAME_AVAILABLE
        
        if not self.enabled:
            if not PYGAME_AVAILABLE:
                logger.info("Sound alerts disabled (pygame not available)")
            else:
                logger.info("Sound alerts disabled in config")
            return
        
        sound_config = config.get('SOUND_CONFIG', {})
        
        # Get sound file paths
        self.get_ready_sound = sound_config.get('get_ready_sound', 'sounds/get_ready.mp3')
        self.almost_ready_sound = sound_config.get('almost_ready_sound', 'sounds/almost_ready.mp3')
        self.big_bang_sound = sound_config.get('big_bang_sound', 'sounds/big_bang.mp3')
        self.volume = sound_config.get('volume', 0.8)
        
        # Set volume
        pygame.mixer.music.set_volume(self.volume)
        
        logger.info(f"Sound player initialized (Volume: {self.volume})")
    
    def play_sound(self, sound_file: str) -> bool:
        """
        Play a sound file
        
        Args:
            sound_file: Path to sound file
            
        Returns:
            bool: True if played successfully
        """
        if not self.enabled:
            return False
        
        try:
            if not Path(sound_file).exists():
                logger.warning(f"Sound file not found: {sound_file}")
                # Try to play system beep as fallback
                self._play_system_beep()
                return False
            
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
            
            logger.info(f"Playing sound: {sound_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error playing sound: {e}")
            self._play_system_beep()
            return False
    
    def _play_system_beep(self):
        """Play system beep as fallback"""
        try:
            import winsound
            winsound.Beep(1000, 500)  # Frequency 1000Hz, duration 500ms
        except:
            try:
                import os
                os.system('beep')  # Linux
            except:
                print('\a')  # ASCII bell
    
    def play_alert(self, level: str) -> bool:
        """
        Play alert sound for specific level
        
        Args:
            level: Alert level ('get_ready', 'almost_ready', 'big_bang')
            
        Returns:
            bool: True if played successfully
        """
        if not self.enabled:
            return False
        
        sound_map = {
            'get_ready': self.get_ready_sound,
            'almost_ready': self.almost_ready_sound,
            'big_bang': self.big_bang_sound
        }
        
        sound_file = sound_map.get(level)
        if sound_file:
            return self.play_sound(sound_file)
        else:
            logger.warning(f"Unknown alert level: {level}")
            return False
    
    def play_alerts_batch(self, alerts: Dict[str, List[Dict]]) -> bool:
        """
        Play sounds for batch of alerts
        Only plays the highest priority alert sound
        
        Args:
            alerts: Dictionary of alerts by level
            
        Returns:
            bool: True if any sound played
        """
        if not self.enabled:
            return False
        
        # Priority: Big Bang > Almost Ready > Get Ready
        if alerts.get('big_bang'):
            return self.play_alert('big_bang')
        elif alerts.get('almost_ready'):
            return self.play_alert('almost_ready')
        elif alerts.get('get_ready'):
            return self.play_alert('get_ready')
        
        return False
    
    def test_sounds(self) -> bool:
        """
        Test all sound files
        
        Returns:
            bool: True if all sounds available
        """
        if not self.enabled:
            logger.warning("Sound alerts disabled")
            return False
        
        logger.info("Testing sound files...")
        
        success_count = 0
        
        for level, sound_file in [
            ('get_ready', self.get_ready_sound),
            ('almost_ready', self.almost_ready_sound),
            ('big_bang', self.big_bang_sound)
        ]:
            if Path(sound_file).exists():
                logger.info(f"✅ {level}: {sound_file}")
                success_count += 1
            else:
                logger.warning(f"❌ {level}: {sound_file} NOT FOUND")
        
        if success_count == 0:
            logger.warning("No sound files found! Using system beep as fallback.")
            logger.info("\nTo add custom sounds:")
            logger.info("1. Create 'sounds/' directory in scanner root")
            logger.info("2. Add these files:")
            logger.info("   - get_ready.mp3 (60% alert)")
            logger.info("   - almost_ready.mp3 (70% alert)")
            logger.info("   - big_bang.mp3 (80% entry)")
            logger.info("3. Or update paths in config.py")
        
        return success_count == 3
    
    def set_volume(self, volume: float):
        """
        Set playback volume
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if not self.enabled:
            return
        
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
        logger.info(f"Volume set to {self.volume}")
