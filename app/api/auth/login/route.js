import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

export async function POST(req) {
  try {
    const body = await req.json();
    let username = body.username;
    let password = body.password;

    // Support FormData for login form which uses x-www-form-urlencoded sometimes in FastAPI
    if (!username && req.headers.get('content-type')?.includes('form-data')) {
      const formData = await req.formData();
      username = formData.get('username');
      password = formData.get('password');
    }

    if (!username || !password) {
      return NextResponse.json({ detail: "Missing username or password" }, { status: 400 });
    }

    const lowerUser = username.toLowerCase();
    const result = await query('SELECT * FROM users WHERE LOWER(username) = $1', [lowerUser]);
    
    if (result.rows.length === 0) {
      return NextResponse.json({ detail: "Invalid username or password" }, { status: 401 });
    }

    const user = result.rows[0];
    const isValid = await bcrypt.compare(password, user.password_hash);
    if (!isValid) {
      return NextResponse.json({ detail: "Invalid username or password" }, { status: 401 });
    }

    // Create JWT
    const token = jwt.sign({ sub: user.id }, process.env.JWT_SECRET || 'fallback_secret', { expiresIn: '7d' });

    return NextResponse.json({ access_token: token, token_type: "bearer" });
  } catch (error) {
    console.error("Login error:", error);
    return NextResponse.json({ detail: "Login failed" }, { status: 500 });
  }
}
