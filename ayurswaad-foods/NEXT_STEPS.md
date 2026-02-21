# What's Next? - Ayurswaad Foods Roadmap

Congratulations on launching the local version of **Ayurswaad Foods**! 🎉
To transform this project into a real-world business, follow these steps:

## 1. Customize Content (Images & Text)
*   **Images:** Replace the placeholder images in `public/` with your real product photos.
    *   Place your images in the `public/images/` folder (e.g., `besan-laddu.jpg`).
    *   Update the file names in `prisma/seed.js` to match your new images.
    *   Run `node prisma/seed.js` again to update the database.
*   **Text:** Edit `app/page.tsx` to change the "Our Story" text and "Why Choose Us" sections with your specific brand messaging.
*   **Contact Info:** Update `app/contact/page.tsx` (if created) or the Footer in `components/layout/Footer.tsx` with your real phone number and email.

## 2. Connect Real Database (Supabase)
Currently, the app uses a local SQLite file (`dev.db`). For a live website, you need a cloud database.
1.  Create a project on [Supabase](https://supabase.com).
2.  Get your **Connection String** from Settings > Database.
3.  Update `prisma/schema.prisma`:
    ```prisma
    datasource db {
      provider = "postgresql" // Change from "sqlite"
      url      = env("DATABASE_URL")
    }
    ```
4.  Create a `.env` file with `DATABASE_URL="your_supabase_connection_string"`.
5.  Run `npx prisma db push` to create the tables in the cloud.

## 3. Integrate Real Payments (Razorpay)
Currently, the checkout is a simulation. To take real money:
1.  Sign up for [Razorpay](https://razorpay.com).
2.  Get your **Key ID** and **Key Secret**.
3.  Install the Razorpay SDK: `npm install razorpay`.
4.  Update `app/cart/page.tsx` to use the Razorpay Checkout script instead of the mock `setTimeout`.
5.  Refer to the [Razorpay Next.js Integration Guide](https://razorpay.com/docs/payment-gateway/web-integration/standard/nextjs/).

## 4. Go Live (Deployment)
1.  Push your code to **GitHub**.
2.  Connect your repository to **Vercel** (see `DEPLOYMENT.md`).
3.  Add your Environment Variables in Vercel settings (`DATABASE_URL`, `RAZORPAY_KEY`, etc.).
4.  Click **Deploy**.

## 5. Marketing & SEO
*   **Metadata:** Update `app/layout.tsx` with your real SEO keywords and description.
*   **Analytics:** Add Google Analytics script to `app/layout.tsx`.
*   **Social Media:** Create Instagram/Facebook pages and link them in the Footer.

Good luck with your business! 🚀
