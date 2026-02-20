# Deployment Guide for Ayurswaad Foods

## 1. Prerequisites
- GitHub Account
- Vercel Account
- Supabase Account

## 2. Database Setup (Supabase)
1. Log in to [Supabase](https://supabase.com/).
2. Create a new project named `ayurswaad-foods`.
3. Go to **Settings > Database** and copy the **Connection String (URI)**. It looks like:
   `postgresql://postgres:[PASSWORD]@db.xxxx.supabase.co:5432/postgres`
4. Go to **SQL Editor** and paste the content of `SCHEMA.sql` (found in the root of this repo) to create the tables.
5. Click **Run**.

## 3. Environment Variables
You need to set the following environment variable in your deployment environment:
- `DATABASE_URL`: The Supabase connection string from step 2.

## 4. Deploy to Vercel
1. Push this code to a GitHub repository.
2. Log in to [Vercel](https://vercel.com/).
3. Click **Add New > Project**.
4. Import the `ayurswaad-foods` repository.
5. In the **Configure Project** step:
   - **Framework Preset**: Next.js
   - **Root Directory**: `ayurswaad-foods` (if it's in a subdirectory) or `./`.
   - **Environment Variables**: Add `DATABASE_URL` with your Supabase string.
6. Click **Deploy**.

## 5. Post-Deployment
1. Once deployed, your site will be live at `https://your-project.vercel.app`.
2. To seed the initial products in Supabase (optional):
   - You can run the seed script locally pointing to the remote DB (update .env locally).
   - Or manually insert rows using Supabase Table Editor.

## 6. Domain Connection
1. Buy a domain (e.g., `ayurswaadfoods.com`) from GoDaddy or similar.
2. In Vercel, go to **Settings > Domains**.
3. Enter your domain name and click **Add**.
4. Follow the instructions to update nameservers or DNS records (A record / CNAME) in your domain registrar.

## 7. Payment Gateway Integration
Currently, the app uses a Mock Payment Gateway. To integrate Razorpay:
1. Sign up for Razorpay.
2. Get API Key and Secret.
3. Update `app/cart/page.tsx` to use Razorpay Checkout SDK instead of the mock `setTimeout`.
4. Create a new API route `app/api/payment/order/route.ts` to create Razorpay orders on the server.

## 8. Backup Instructions
1. **Database**: Supabase provides automated daily backups on the Pro plan. On the Free plan, you can manually export your data.
   - Go to **Database > Backups**.
   - Click **Download** or run `pg_dump` via CLI.
2. **Code**: Your code is versioned on GitHub. Ensure regular commits.
3. **Images**: If using Supabase Storage for images, ensure you have a local copy of original assets.
