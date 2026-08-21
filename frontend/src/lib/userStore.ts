import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

export interface StoredUser {
  id: string;
  name: string;
  email: string;
  passwordHash: string;
  createdAt: string;
}

const DATA_DIR = path.join(process.cwd(), 'data');
const USERS_FILE = path.join(DATA_DIR, 'users.json');

// Helper to hash passwords securely using SHA-256
export function hashPassword(password: string): string {
  return crypto.createHash('sha256').update(password).digest('hex');
}

// Ensure the data directory and users.json file exist
function ensureUsersFileExists(): void {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }

  if (!fs.existsSync(USERS_FILE)) {
    // Initialize with an empty array or demo account
    const initialUsers: StoredUser[] = [];
    fs.writeFileSync(USERS_FILE, JSON.stringify(initialUsers, null, 2), 'utf-8');
  }
}

// Read all users from disk
export function getAllUsers(): StoredUser[] {
  try {
    ensureUsersFileExists();
    const data = fs.readFileSync(USERS_FILE, 'utf-8');
    return JSON.parse(data) as StoredUser[];
  } catch (error) {
    console.error('Error reading users file:', error);
    return [];
  }
}

// Find a user by normalized email
export function getUserByEmail(email: string): StoredUser | null {
  const normalized = email.trim().toLowerCase();
  const users = getAllUsers();
  return users.find((u) => u.email.toLowerCase() === normalized) || null;
}

// Create a new user and persist to disk
export function createUser(userData: {
  name: string;
  email: string;
  password: string;
}): StoredUser {
  ensureUsersFileExists();
  const normalizedEmail = userData.email.trim().toLowerCase();

  const existing = getUserByEmail(normalizedEmail);
  if (existing) {
    throw new Error('An account with this email address already exists.');
  }

  const newUser: StoredUser = {
    id: 'usr_' + crypto.randomUUID().substring(0, 8),
    name: userData.name.trim(),
    email: normalizedEmail,
    passwordHash: hashPassword(userData.password),
    createdAt: new Date().toISOString(),
  };

  const users = getAllUsers();
  users.push(newUser);
  fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2), 'utf-8');

  return newUser;
}

// Verify credentials during login
export function verifyUser(
  email: string,
  password: string
): { id: string; name: string; email: string } | null {
  const user = getUserByEmail(email);
  if (!user) {
    return null;
  }

  const hash = hashPassword(password);
  if (user.passwordHash !== hash) {
    return null;
  }

  return {
    id: user.id,
    name: user.name,
    email: user.email,
  };
}
