import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import bcrypt from 'bcryptjs';
import { signJWT } from '@/lib/auth';
import { cookies } from 'next/headers';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { email, password, otp, type } = body;

    // Simulate OTP Request
    if (type === 'otp-request') {
      if (!email) {
        return NextResponse.json({ error: 'Email is required' }, { status: 400 });
      }
      // Check if user exists, if not create a temporary record or just allow
      // For now, we simulate sending an OTP.
      console.log(`[OTP Simulation] OTP for ${email} is 123456`);
      return NextResponse.json({ message: 'OTP sent successfully' });
    }

    let user = null;

    // OTP Verification Flow
    if (otp) {
      if (otp !== '123456') {
        return NextResponse.json({ error: 'Invalid OTP' }, { status: 401 });
      }

      // Find or Create User for OTP login
      user = await prisma.user.findUnique({ where: { email } });
      if (!user) {
        // Create a new user with random password if logging in via OTP for first time
        const hashedPassword = await bcrypt.hash(Math.random().toString(36), 10);
        user = await prisma.user.create({
          data: {
            email,
            password: hashedPassword,
            name: email.split('@')[0],
            role: 'USER',
          },
        });
      }
    }
    // Password Verification Flow
    else if (password) {
      user = await prisma.user.findUnique({ where: { email } });
      if (!user || !(await bcrypt.compare(password, user.password))) {
        return NextResponse.json({ error: 'Invalid email or password' }, { status: 401 });
      }
    } else {
      return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
    }

    // Generate JWT
    const token = await signJWT({
      id: user.id,
      email: user.email,
      role: user.role
    });

    // Set Cookie
    const cookieStore = await cookies();
    cookieStore.set('token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/',
      maxAge: 60 * 60 * 24, // 24 hours
    });

    return NextResponse.json({
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role
      }
    });

  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
