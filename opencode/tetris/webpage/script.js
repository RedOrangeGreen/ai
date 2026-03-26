const COLS = 10;
const ROWS = 20;
const BLOCK_SIZE = 30;
const PREVIEW_BLOCK_SIZE = 20;

const TETROMINOES = {
    I: { color: '#00f0f0', shape: [[1,1,1,1]] },
    O: { color: '#f0f000', shape: [[1,1],[1,1]] },
    T: { color: '#a000f0', shape: [[0,1,0],[1,1,1]] },
    S: { color: '#00f000', shape: [[0,1,1],[1,1,0]] },
    Z: { color: '#f00000', shape: [[1,1,0],[0,1,1]] },
    J: { color: '#0000f0', shape: [[1,0,0],[1,1,1]] },
    L: { color: '#f0a000', shape: [[0,0,1],[1,1,1]] }
};

const POINTS = {
    1: 100,
    2: 300,
    3: 500,
    4: 800
};

const LEVEL_SPEED = {
    1: 1000, 2: 900, 3: 800, 4: 700, 5: 600,
    6: 500, 7: 400, 8: 300, 9: 200, 10: 100
};

class AudioManager {
    constructor() {
        this.ctx = null;
        this.masterGain = null;
        this.musicGain = null;
        this.sfxGain = null;
        this.muted = false;
        this.musicMuted = false;
        this.initialized = false;
        this.sequencerInterval = null;
        this.currentBeat = 0;
        this.bpm = 120;
        this.baseBpm = 120;
    }
    
    init() {
        if (this.initialized) return;
        this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        this.masterGain = this.ctx.createGain();
        this.musicGain = this.ctx.createGain();
        this.sfxGain = this.ctx.createGain();
        this.masterGain.connect(this.ctx.destination);
        this.musicGain.connect(this.masterGain);
        this.sfxGain.connect(this.masterGain);
        this.targetVolume = 1.0;
        this.masterGain.gain.value = this.targetVolume;
        this.musicGain.gain.value = 0.4;
        this.sfxGain.gain.value = 0.7;
        this.initialized = true;
    }
    
    toggleMute() {
        this.muted = !this.muted;
        this.masterGain.gain.setTargetAtTime(this.muted ? 0 : this.targetVolume, this.ctx.currentTime, 0.1);
        return this.muted;
    }
    
    setVolume(volume) {
        this.targetVolume = volume;
        if (!this.muted) {
            this.masterGain.gain.setTargetAtTime(this.targetVolume, this.ctx.currentTime, 0.1);
        }
    }
    
    startMusic(level = 1) {
        if (!this.initialized || this.musicMuted) return;
        this.stopMusic();
        this.bpm = this.baseBpm + (level - 1) * 5;
        this.currentBeat = 0;
        const interval = (60 / this.bpm) * 1000 / 2;
        this.sequencerInterval = setInterval(() => this.tick(), interval);
    }
    
    stopMusic() {
        if (this.sequencerInterval) {
            clearInterval(this.sequencerInterval);
            this.sequencerInterval = null;
        }
    }
    
    tick() {
        if (!this.initialized || this.musicMuted) return;
        const beat = this.currentBeat % 16;
        
        if (beat % 4 === 0) this.playKick();
        if (beat % 4 === 2) this.playHiHat();
        if (beat % 2 === 0) this.playBass(beat);
        if (beat % 4 === 0) this.playMelody(beat);
        
        this.currentBeat++;
    }
    
    playKick() {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(150, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(40, this.ctx.currentTime + 0.1);
        gain.gain.setValueAtTime(0.5, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.2);
        osc.connect(gain);
        gain.connect(this.musicGain);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.2);
    }
    
    playHiHat() {
        const bufferSize = this.ctx.sampleRate * 0.05;
        const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            data[i] = Math.random() * 2 - 1;
        }
        const noise = this.ctx.createBufferSource();
        noise.buffer = buffer;
        const filter = this.ctx.createBiquadFilter();
        filter.type = 'highpass';
        filter.frequency.value = 8000;
        const gain = this.ctx.createGain();
        gain.gain.setValueAtTime(0.1, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.05);
        noise.connect(filter);
        filter.connect(gain);
        gain.connect(this.musicGain);
        noise.start();
    }
    
    playBass(beat) {
        const bassNotes = [55, 55, 73.42, 65.41];
        const noteIndex = Math.floor(beat / 4) % bassNotes.length;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'square';
        osc.frequency.value = bassNotes[noteIndex];
        gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.15);
        osc.connect(gain);
        gain.connect(this.musicGain);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.15);
    }
    
    playMelody(beat) {
        const melodyPattern = [
            [329.63, 0.1], [392.00, 0.1], [440.00, 0.1], [329.63, 0.1],
            [493.88, 0.1], [440.00, 0.1], [392.00, 0.1], [329.63, 0.1],
            [523.25, 0.15], [493.88, 0.05], [440.00, 0.1], [392.00, 0.1],
            [329.63, 0.1], [293.66, 0.1], [329.63, 0.2]
        ];
        const noteIndex = Math.floor(beat / 4) % melodyPattern.length;
        const [freq, dur] = melodyPattern[noteIndex];
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + dur);
        osc.connect(gain);
        gain.connect(this.musicGain);
        osc.start();
        osc.stop(this.ctx.currentTime + dur);
    }
    
    playMove() {
        if (!this.initialized) return;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'square';
        osc.frequency.value = 800;
        gain.gain.setValueAtTime(0.05, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.03);
        osc.connect(gain);
        gain.connect(this.sfxGain);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.03);
    }
    
    playRotate() {
        if (!this.initialized) return;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(400, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(600, this.ctx.currentTime + 0.05);
        gain.gain.setValueAtTime(0.1, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.08);
        osc.connect(gain);
        gain.connect(this.sfxGain);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.08);
    }
    
    playSoftDrop() {
        if (!this.initialized) return;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.value = 200;
        gain.gain.setValueAtTime(0.03, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.05);
        osc.connect(gain);
        gain.connect(this.sfxGain);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.05);
    }
    
    playHardDrop() {
        if (!this.initialized) return;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(150, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(50, this.ctx.currentTime + 0.15);
        gain.gain.setValueAtTime(0.3, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.15);
        osc.connect(gain);
        gain.connect(this.sfxGain);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.15);
    }
    
    playLock() {
        if (!this.initialized) return;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.value = 200;
        gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.1);
        osc.connect(gain);
        gain.connect(this.sfxGain);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.1);
    }
    
    playLineClear(lines) {
        if (!this.initialized) return;
        const baseFreq = 440;
        const freqs = lines >= 4 ? [523.25, 659.25, 783.99, 1046.50] :
                      lines === 3 ? [523.25, 659.25, 783.99] :
                      lines === 2 ? [523.25, 659.25] : [523.25];
        
        freqs.forEach((freq, i) => {
            setTimeout(() => {
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.type = 'square';
                osc.frequency.value = freq;
                gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.2);
                osc.connect(gain);
                gain.connect(this.sfxGain);
                osc.start();
                osc.stop(this.ctx.currentTime + 0.2);
            }, i * 50);
        });
    }
    
    playGameOver() {
        if (!this.initialized) return;
        const notes = [440, 349.23, 293.66, 220];
        notes.forEach((freq, i) => {
            setTimeout(() => {
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.value = freq;
                gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.3);
                osc.connect(gain);
                gain.connect(this.sfxGain);
                osc.start();
                osc.stop(this.ctx.currentTime + 0.3);
            }, i * 150);
        });
    }
    
    playLevelUp() {
        if (!this.initialized) return;
        const notes = [261.63, 329.63, 392.00, 523.25];
        notes.forEach((freq, i) => {
            setTimeout(() => {
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.type = 'square';
                osc.frequency.value = freq;
                gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.15);
                osc.connect(gain);
                gain.connect(this.sfxGain);
                osc.start();
                osc.stop(this.ctx.currentTime + 0.15);
            }, i * 80);
        });
    }
}

class TetrisGame {
    constructor() {
        this.canvas = document.getElementById('game-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.ghostCanvas = document.getElementById('ghost-canvas');
        this.ghostCtx = this.ghostCanvas.getContext('2d');
        this.nextCanvas = document.getElementById('next-canvas');
        this.nextCtx = this.nextCanvas.getContext('2d');
        this.holdCanvas = document.getElementById('hold-canvas');
        this.holdCtx = this.holdCanvas.getContext('2d');
        
        this.canvas.width = COLS * BLOCK_SIZE;
        this.canvas.height = ROWS * BLOCK_SIZE;
        this.ghostCanvas.width = COLS * BLOCK_SIZE;
        this.ghostCanvas.height = ROWS * BLOCK_SIZE;
        this.nextCanvas.width = 4 * PREVIEW_BLOCK_SIZE;
        this.nextCanvas.height = 4 * PREVIEW_BLOCK_SIZE;
        this.holdCanvas.width = 4 * PREVIEW_BLOCK_SIZE;
        this.holdCanvas.height = 4 * PREVIEW_BLOCK_SIZE;
        
        this.audio = new AudioManager();
        this.board = [];
        this.pieces = [];
        this.currentPiece = null;
        this.nextPiece = null;
        this.holdPiece = null;
        this.canHold = true;
        this.score = 0;
        this.level = 1;
        this.lines = 0;
        this.combo = 0;
        this.gameState = 'start';
        this.dropInterval = null;
        this.lockDelay = 500;
        this.lastMove = 0;
        this.animationId = null;
        
        this.startScreen = document.getElementById('start-screen');
        this.pauseScreen = document.getElementById('pause-screen');
        this.gameOverScreen = document.getElementById('game-over-screen');
        this.finalScoreEl = document.getElementById('final-score');
        this.scoreEl = document.getElementById('score');
        this.levelEl = document.getElementById('level');
        this.linesEl = document.getElementById('lines');
        this.audioStatusEl = document.getElementById('audio-status');
        this.lineClearOverlay = document.getElementById('line-clear-overlay');
        this.volumeSlider = document.getElementById('volume-slider');
        
        this.init();
    }
    
    init() {
        this.setupInputs();
        this.setupVolumeControl();
        this.render();
    }
    
    setupVolumeControl() {
        this.volumeSlider.addEventListener('input', (e) => {
            const sliderValue = e.target.value;
            const minVolume = 0.3;
            const maxVolume = 1.0;
            const volume = minVolume + (sliderValue / 100) * (maxVolume - minVolume);
            this.audio.setVolume(volume);
        });
        this.volumeSlider.addEventListener('keydown', (e) => {
            e.stopPropagation();
        });
    }
    
    setupInputs() {
        document.addEventListener('keydown', (e) => {
            if (this.gameState === 'start') {
                if (e.key === 'Enter') this.startGame();
                return;
            }
            if (this.gameState === 'gameover') {
                if (e.key === 'Enter') this.restart();
                return;
            }
            if (e.key === 'p' || e.key === 'P') {
                this.togglePause();
                return;
            }
            if (e.key === 'm' || e.key === 'M') {
                this.toggleAudio();
                return;
            }
            if (this.gameState !== 'playing') return;
            
            switch(e.key) {
                case 'ArrowLeft':
                    this.movePiece(-1);
                    break;
                case 'ArrowRight':
                    this.movePiece(1);
                    break;
                case 'ArrowUp':
                    this.rotatePiece();
                    break;
                case 'ArrowDown':
                    this.softDrop();
                    break;
                case ' ':
                    e.preventDefault();
                    this.hardDrop();
                    break;
                case 'c':
                case 'C':
                    this.holdCurrentPiece();
                    break;
            }
        });
    }
    
    toggleAudio() {
        const muted = this.audio.toggleMute();
        this.audioStatusEl.textContent = muted ? '🔇 MUTED' : '🔊 ON';
        if (!muted && this.gameState === 'playing') {
            this.audio.startMusic(this.level);
        } else {
            this.audio.stopMusic();
        }
    }
    
    startGame() {
        this.audio.init();
        this.audio.startMusic(1);
        this.resetBoard();
        this.fillBag();
        this.nextPiece = this.getNextFromBag();
        this.spawnPiece();
        this.gameState = 'playing';
        this.startDropTimer();
        this.startScreen.classList.add('hidden');
        this.gameOverScreen.classList.add('hidden');
        this.startAnimation();
    }
    
    restart() {
        this.score = 0;
        this.level = 1;
        this.lines = 0;
        this.combo = 0;
        this.holdPiece = null;
        this.canHold = true;
        this.updateDisplay();
        this.startGame();
    }
    
    resetBoard() {
        this.board = Array(ROWS).fill(null).map(() => Array(COLS).fill(0));
    }
    
    fillBag() {
        this.pieces = Object.keys(TETROMINOES).sort(() => Math.random() - 0.5);
    }
    
    getNextFromBag() {
        if (this.pieces.length === 0) this.fillBag();
        return this.pieces.pop();
    }
    
    spawnPiece() {
        this.currentPiece = this.nextPiece;
        this.currentPieceShape = null;
        this.nextPiece = this.getNextFromBag();
        this.currentX = Math.floor(COLS / 2) - Math.floor(TETROMINOES[this.currentPiece].shape.length / 2);
        this.currentY = 0;
        this.canHold = true;
        this.renderNextPreview();
        if (this.checkCollision(this.currentX, this.currentY, TETROMINOES[this.currentPiece].shape)) {
            this.gameOver();
        }
    }
    
    getPieceShape() {
        if (this.currentPieceShape) return this.currentPieceShape;
        return TETROMINOES[this.currentPiece].shape;
    }
    
    getPieceColor() {
        return TETROMINOES[this.currentPiece].color;
    }
    
    checkCollision(x, y, shape) {
        for (let row = 0; row < shape.length; row++) {
            for (let col = 0; col < shape[row].length; col++) {
                if (shape[row][col]) {
                    const newX = x + col;
                    const newY = y + row;
                    if (newX < 0 || newX >= COLS || newY >= ROWS) return true;
                    if (newY >= 0 && this.board[newY][newX]) return true;
                }
            }
        }
        return false;
    }
    
    movePiece(dir) {
        const newX = this.currentX + dir;
        if (!this.checkCollision(newX, this.currentY, this.getPieceShape())) {
            this.currentX = newX;
            this.audio.playMove();
        }
    }
    
    rotatePiece() {
        const shape = this.getPieceShape();
        const rotated = shape[0].map((_, i) => shape.map(row => row[i]).reverse());
        const kicks = [[0, 0], [-1, 0], [1, 0], [0, -1], [-2, 0], [2, 0]];
        for (const [dx, dy] of kicks) {
            if (!this.checkCollision(this.currentX + dx, this.currentY + dy, rotated)) {
                this.currentPieceShape = rotated;
                this.currentX += dx;
                this.currentY += dy;
                this.audio.playRotate();
                return;
            }
        }
    }
    
    softDrop() {
        if (!this.checkCollision(this.currentX, this.currentY + 1, this.getPieceShape())) {
            this.currentY++;
            this.audio.playSoftDrop();
        }
    }
    
    hardDrop() {
        while (!this.checkCollision(this.currentX, this.currentY + 1, this.getPieceShape())) {
            this.currentY++;
        }
        this.audio.playHardDrop();
        this.lockPiece();
    }
    
    holdCurrentPiece() {
        if (!this.canHold) return;
        this.canHold = false;
        if (this.holdPiece === null) {
            this.holdPiece = this.currentPiece;
            this.spawnPiece();
        } else {
            const temp = this.holdPiece;
            this.holdPiece = this.currentPiece;
            this.currentPiece = temp;
            this.currentPieceShape = null;
            this.currentX = Math.floor(COLS / 2) - Math.floor(TETROMINOES[this.currentPiece].shape.length / 2);
            this.currentY = 0;
        }
        this.audio.playRotate();
        this.renderHoldPreview();
    }
    
    startDropTimer() {
        if (this.dropInterval) clearInterval(this.dropInterval);
        const speed = LEVEL_SPEED[this.level] || 100;
        this.dropInterval = setInterval(() => {
            if (this.gameState === 'playing') {
                this.dropPiece();
            }
        }, speed);
    }
    
    dropPiece() {
        if (!this.checkCollision(this.currentX, this.currentY + 1, this.getPieceShape())) {
            this.currentY++;
        } else {
            this.startLockDelay();
        }
    }
    
    startLockDelay() {
        if (this.lockTimer) return;
        this.lockTimer = setTimeout(() => {
            this.lockPiece();
            this.lockTimer = null;
        }, this.lockDelay);
    }
    
    lockPiece() {
        if (this.lockTimer) {
            clearTimeout(this.lockTimer);
            this.lockTimer = null;
        }
        const shape = this.getPieceShape();
        const color = this.getPieceColor();
        for (let row = 0; row < shape.length; row++) {
            for (let col = 0; col < shape[row].length; col++) {
                if (shape[row][col]) {
                    const y = this.currentY + row;
                    const x = this.currentX + col;
                    if (y >= 0) {
                        this.board[y][x] = color;
                    }
                }
            }
        }
        this.audio.playLock();
        this.clearLines();
        this.spawnPiece();
    }
    
    clearLines() {
        let linesCleared = 0;
        for (let row = ROWS - 1; row >= 0; row--) {
            const isFull = this.board[row].every(cell => cell !== 0);
            if (isFull) {
                this.board.splice(row, 1);
                this.board.unshift(Array(COLS).fill(0));
                linesCleared++;
                row++;
            }
        }
        if (linesCleared > 0) {
            this.lines += linesCleared;
            const prevLevel = this.level;
            this.level = Math.floor(this.lines / 10) + 1;
            if (this.level > prevLevel) {
                this.audio.playLevelUp();
                this.startDropTimer();
            }
            this.combo++;
            const points = POINTS[linesCleared] * this.level;
            const comboBonus = this.combo > 1 ? this.combo * 50 : 0;
            this.score += points + comboBonus;
            this.audio.playLineClear(linesCleared);
            this.showLineClearEffect(linesCleared);
            if (this.combo > 1) {
                this.showComboText(this.combo);
            }
            this.updateDisplay();
        } else {
            this.combo = 0;
        }
    }
    
    showLineClearEffect(lines) {
        this.lineClearOverlay.classList.remove('active');
        void this.lineClearOverlay.offsetWidth;
        this.lineClearOverlay.classList.add('active');
        this.createParticles(lines);
    }
    
    createParticles(lines) {
        const container = document.createElement('div');
        container.className = 'particles';
        const rect = this.canvas.getBoundingClientRect();
        container.style.left = rect.left + 'px';
        container.style.top = rect.top + rect.height / 2 + 'px';
        document.body.appendChild(container);
        
        for (let i = 0; i < lines * 20; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.background = this.getPieceColor();
            particle.style.left = Math.random() * rect.width + 'px';
            particle.style.setProperty('--dx', (Math.random() - 0.5) * 200 + 'px');
            particle.style.setProperty('--dy', (Math.random() - 0.5) * 200 + 'px');
            container.appendChild(particle);
        }
        
        setTimeout(() => container.remove(), 600);
    }
    
    showComboText(combo) {
        const existing = document.querySelector('.combo-text');
        if (existing) existing.remove();
        
        const comboEl = document.createElement('div');
        comboEl.className = 'combo-text';
        comboEl.textContent = `${combo} COMBO!`;
        const rect = this.canvas.getBoundingClientRect();
        comboEl.style.left = rect.left + rect.width / 2 - 50 + 'px';
        comboEl.style.top = rect.top + rect.height / 2 + 'px';
        document.body.appendChild(comboEl);
        
        setTimeout(() => comboEl.remove(), 800);
    }
    
    updateDisplay() {
        this.scoreEl.textContent = this.score;
        this.levelEl.textContent = this.level;
        this.linesEl.textContent = this.lines;
    }
    
    gameOver() {
        this.gameState = 'gameover';
        this.audio.stopMusic();
        this.audio.playGameOver();
        if (this.dropInterval) clearInterval(this.dropInterval);
        if (this.animationId) cancelAnimationFrame(this.animationId);
        this.finalScoreEl.textContent = `Score: ${this.score}`;
        this.gameOverScreen.classList.remove('hidden');
    }
    
    togglePause() {
        if (this.gameState === 'playing') {
            this.gameState = 'paused';
            this.audio.stopMusic();
            if (this.dropInterval) clearInterval(this.dropInterval);
            this.pauseScreen.classList.remove('hidden');
        } else if (this.gameState === 'paused') {
            this.gameState = 'playing';
            this.audio.startMusic(this.level);
            this.startDropTimer();
            this.pauseScreen.classList.add('hidden');
        }
    }
    
    startAnimation() {
        const animate = () => {
            if (this.gameState === 'playing' || this.gameState === 'paused') {
                this.render();
                this.animationId = requestAnimationFrame(animate);
            }
        };
        animate();
    }
    
    render() {
        this.ctx.fillStyle = '#0a0a15';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        this.renderGrid();
        this.renderBoard();
        this.renderGhostPiece();
        this.renderCurrentPiece();
    }
    
    renderGrid() {
        this.ctx.strokeStyle = 'rgba(0, 255, 255, 0.1)';
        this.ctx.lineWidth = 1;
        for (let x = 0; x <= COLS; x++) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * BLOCK_SIZE, 0);
            this.ctx.lineTo(x * BLOCK_SIZE, this.canvas.height);
            this.ctx.stroke();
        }
        for (let y = 0; y <= ROWS; y++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y * BLOCK_SIZE);
            this.ctx.lineTo(this.canvas.width, y * BLOCK_SIZE);
            this.ctx.stroke();
        }
    }
    
    renderBoard() {
        for (let row = 0; row < ROWS; row++) {
            for (let col = 0; col < COLS; col++) {
                if (this.board[row][col]) {
                    this.drawBlock(this.ctx, col, row, this.board[row][col], BLOCK_SIZE);
                }
            }
        }
    }
    
    renderCurrentPiece() {
        const shape = this.getPieceShape();
        const color = this.getPieceColor();
        for (let row = 0; row < shape.length; row++) {
            for (let col = 0; col < shape[row].length; col++) {
                if (shape[row][col]) {
                    this.drawBlock(this.ctx, this.currentX + col, this.currentY + row, color, BLOCK_SIZE);
                }
            }
        }
    }
    
    renderGhostPiece() {
        let ghostY = this.currentY;
        while (!this.checkCollision(this.currentX, ghostY + 1, this.getPieceShape())) {
            ghostY++;
        }
        if (ghostY !== this.currentY) {
            const shape = this.getPieceShape();
            this.ghostCtx.clearRect(0, 0, this.ghostCanvas.width, this.ghostCanvas.height);
            this.ghostCtx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
            this.ghostCtx.lineWidth = 2;
            for (let row = 0; row < shape.length; row++) {
                for (let col = 0; col < shape[row].length; col++) {
                    if (shape[row][col]) {
                        const x = (this.currentX + col) * BLOCK_SIZE;
                        const y = (ghostY + row) * BLOCK_SIZE;
                        this.ghostCtx.strokeRect(x + 2, y + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4);
                    }
                }
            }
        } else {
            this.ghostCtx.clearRect(0, 0, this.ghostCanvas.width, this.ghostCanvas.height);
        }
    }
    
    renderNextPreview() {
        this.nextCtx.fillStyle = '#0a0a15';
        this.nextCtx.fillRect(0, 0, this.nextCanvas.width, this.nextCanvas.height);
        if (this.nextPiece) {
            const shape = TETROMINOES[this.nextPiece].shape;
            const color = TETROMINOES[this.nextPiece].color;
            const offsetX = (4 - shape[0].length) / 2;
            const offsetY = (4 - shape.length) / 2;
            for (let row = 0; row < shape.length; row++) {
                for (let col = 0; col < shape[row].length; col++) {
                    if (shape[row][col]) {
                        const x = (offsetX + col) * PREVIEW_BLOCK_SIZE;
                        const y = (offsetY + row) * PREVIEW_BLOCK_SIZE;
                        this.drawBlock(this.nextCtx, x / PREVIEW_BLOCK_SIZE, y / PREVIEW_BLOCK_SIZE, color, PREVIEW_BLOCK_SIZE);
                    }
                }
            }
        }
    }
    
    renderHoldPreview() {
        this.holdCtx.fillStyle = '#0a0a15';
        this.holdCtx.fillRect(0, 0, this.holdCanvas.width, this.holdCanvas.height);
        if (this.holdPiece) {
            const shape = TETROMINOES[this.holdPiece].shape;
            const color = TETROMINOES[this.holdPiece].color;
            const offsetX = (4 - shape[0].length) / 2;
            const offsetY = (4 - shape.length) / 2;
            for (let row = 0; row < shape.length; row++) {
                for (let col = 0; col < shape[row].length; col++) {
                    if (shape[row][col]) {
                        const x = (offsetX + col) * PREVIEW_BLOCK_SIZE;
                        const y = (offsetY + row) * PREVIEW_BLOCK_SIZE;
                        this.drawBlock(this.holdCtx, x / PREVIEW_BLOCK_SIZE, y / PREVIEW_BLOCK_SIZE, color, PREVIEW_BLOCK_SIZE);
                    }
                }
            }
        }
    }
    
    drawBlock(ctx, x, y, color, size) {
        const px = x * size;
        const py = y * size;
        ctx.fillStyle = color;
        ctx.fillRect(px + 1, py + 1, size - 2, size - 2);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.fillRect(px + 1, py + 1, size - 2, 4);
        ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        ctx.fillRect(px + 1, py + size - 5, size - 2, 4);
    }
}

const game = new TetrisGame();
