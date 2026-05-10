// AES-256-GCM 動画暗号化スクリプト
// Web Crypto API互換の出力形式（ciphertext + 16byte authTag）
// Usage: node encrypt.js <input> <output> <password>

const crypto = require('crypto');
const fs = require('fs');

const [,, inputPath, outputPath, password] = process.argv;

if (!inputPath || !outputPath || !password) {
  console.error('Usage: node encrypt.js <input> <output> <password>');
  process.exit(1);
}

const salt = crypto.randomBytes(16);
const iv = crypto.randomBytes(12);
const key = crypto.pbkdf2Sync(password, salt, 100000, 32, 'sha256');

const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
const plaintext = fs.readFileSync(inputPath);
const ciphertext = Buffer.concat([cipher.update(plaintext), cipher.final()]);
const authTag = cipher.getAuthTag();

const output = Buffer.concat([ciphertext, authTag]);
fs.writeFileSync(outputPath, output);

console.log(JSON.stringify({
  salt: salt.toString('base64'),
  iv: iv.toString('base64'),
  inputSize: plaintext.length,
  outputSize: output.length,
  outputPath: outputPath
}));
