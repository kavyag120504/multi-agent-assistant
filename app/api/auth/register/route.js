import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import bcrypt from 'bcryptjs';

export async function POST(req) {
  try {
    const { username, display_name, password } = await req.json();

    if (!username || !password || !display_name) {
      return NextResponse.json({ detail: "Missing fields" }, { status: 400 });
    }

    const lowerUser = username.toLowerCase();

    // Check if user exists
    const existing = await query('SELECT * FROM users WHERE LOWER(username) = $1', [lowerUser]);
    if (existing.rows.length > 0) {
      return NextResponse.json({ detail: "Username is already taken." }, { status: 400 });
    }

    // Hash password
    const hash = await bcrypt.hash(password, 10);

    // Insert user
    await query(
      'INSERT INTO users (username, display_name, password_hash) VALUES ($1, $2, $3)',
      [lowerUser, display_name, hash]
    );

    return NextResponse.json({ success: true, message: "Account created successfully!" });
  } catch (error) {
    console.error("Register error:", error);
    return NextResponse.json({ detail: "Registration failed. Please try again." }, { status: 500 });
  }
}
