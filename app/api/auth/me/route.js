import { NextResponse } from 'next/server';
import { query } from '@/lib/db';
import jwt from 'jsonwebtoken';

export async function GET(req) {
  try {
    const authHeader = req.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
    }

    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback_secret');
    
    const result = await query('SELECT id, username, display_name FROM users WHERE id = $1', [decoded.sub]);
    if (result.rows.length === 0) {
      return NextResponse.json({ detail: "User not found" }, { status: 401 });
    }

    return NextResponse.json(result.rows[0]);
  } catch (error) {
    return NextResponse.json({ detail: "Invalid token" }, { status: 401 });
  }
}
