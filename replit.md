# Comic Scene Generator - Django Application

## Project Overview

A Django-based web application that generates comic scenes with dialogue bubbles using AI. Users can register, purchase tokens, and generate custom comic scenes by combining character images with AI-generated scene descriptions.

**Last Updated:** October 19, 2025

## Current State

- **Status:** Fully functional and running
- **Server:** Django 5.2.7 development server on port 5000
- **Database:** PostgreSQL (configured via Replit environment)
- **Workflow:** Django Server running successfully

## Tech Stack

### Backend
- **Framework:** Django 5.2.7
- **Database:** PostgreSQL
- **API Framework:** Django REST Framework
- **Payment Processing:** Stripe
- **AI Services:**
  - Google Gemini API (for scene description generation)
  - Alibaba Qwen-image-edit API (for comic scene composition)

### Frontend
- **Templates:** Django Templates
- **Styling:** Bootstrap 5
- **JavaScript:** Vanilla JS for Stripe integration

### Python Dependencies
- django
- djangorestframework
- psycopg2-binary
- stripe
- google-generativeai
- dashscope
- pydantic
- python-dotenv
- pillow
- requests

## Project Architecture

### Django Apps

1. **accounts** - User authentication and profile management
   - User registration and login
   - User profiles with token balances
   - Token usage tracking

2. **tokens** - Token economy and payment processing
   - Token packages (Starter, Popular, Pro)
   - Stripe checkout integration
   - Purchase history tracking
   - Webhook handling for payment confirmation

3. **generator** - Image generation workflow
   - AI-powered scene description using Gemini
   - Comic scene composition using Qwen
   - Image gallery
   - Generation history

### Database Models

#### UserProfile (accounts app)
- Links to Django User model
- Tracks token balance
- Records total tokens purchased and images generated

#### TokenPackage (tokens app)
- Defines available token packages
- Pricing and token amounts
- Active/inactive status

#### TokenPurchase (tokens app)
- Records all token purchases
- Stripe session/payment intent tracking
- Purchase status (pending/completed/failed/refunded)

#### GeneratedImage (generator app)
- Stores generated comic scenes
- Links to user and dialogue context
- Saves AI-generated prompts and image URLs

## Key Features

### User System
- Registration with username/password
- Login/logout functionality
- User dashboard with statistics
- Profile management

### Token Economy
- Three token packages: Starter (10), Popular (50), Pro (150)
- Secure Stripe payment integration
- Real-time token balance updates
- Purchase history tracking

### Image Generation
- Upload 2 character images + 1 background
- Input scene context and dialogue
- AI generates detailed scene descriptions via Gemini
- Qwen API combines images into comic panel
- Empty speech bubbles for dialogue
- 1 token per generation

## Environment Variables Required

### Required for Full Functionality
- `GEMINI_API_KEY` - Google Gemini API key for scene description
- `IMG_API_KEY` - Alibaba Dashscope API key for image composition
- `STRIPE_SECRET_KEY` - Stripe secret key for payments
- `STRIPE_PUBLISHABLE_KEY` - Stripe publishable key for frontend
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook secret for payment verification

### Auto-configured by Replit
- `DATABASE_URL` - PostgreSQL connection string
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` - Database credentials
- `SESSION_SECRET` - Django secret key

## File Structure

```
.
├── comic_generator/          # Main Django project
│   ├── settings.py          # Project settings
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py
├── accounts/                 # User authentication app
│   ├── models.py            # UserProfile model
│   ├── views.py             # Login/register views
│   ├── admin.py             # Admin configuration
│   └── urls.py
├── tokens/                   # Token management app
│   ├── models.py            # TokenPackage, TokenPurchase
│   ├── views.py             # Purchase flow, Stripe integration
│   ├── admin.py
│   └── urls.py
├── generator/                # Image generation app
│   ├── models.py            # GeneratedImage model
│   ├── views.py             # Generation logic, Gemini & Qwen integration
│   ├── admin.py
│   └── urls.py
├── templates/                # Django templates
│   ├── base.html
│   ├── accounts/            # Login, register templates
│   ├── tokens/              # Package selection, purchase history
│   └── generator/           # Dashboard, generation form, gallery
├── static/                   # Static files (CSS, JS)
├── media/                    # User uploaded images
├── manage.py                 # Django management script
├── setup_defaults.py         # Script to create default token packages
└── replit.md                 # This file
```

## Setup Instructions

### First Time Setup

1. **Install Dependencies** (already done)
   ```bash
   # Dependencies are managed via uv and already installed
   ```

2. **Run Migrations** (already done)
   ```bash
   python manage.py migrate
   ```

3. **Create Default Token Packages** (already done)
   ```bash
   python setup_defaults.py
   ```

4. **Create Admin User** (optional)
   ```bash
   python manage.py createsuperuser
   ```

5. **Configure API Keys**
   - Add GEMINI_API_KEY in Replit Secrets
   - Add IMG_API_KEY in Replit Secrets
   - Add Stripe keys (STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET)

### Running the Application

The Django server is configured to run automatically via Replit workflow on port 5000.

Manual start:
```bash
python manage.py runserver 0.0.0.0:5000
```

## Usage Flow

1. **User Registration**
   - Navigate to /accounts/register/
   - Create account with username and password
   - Automatically logged in with 0 tokens

2. **Purchase Tokens**
   - Go to "Buy Tokens" page
   - Select a token package
   - Complete Stripe checkout
   - Tokens added to balance upon successful payment

3. **Generate Comic Scene**
   - Navigate to "Generate" page
   - Enter scene context (setting, characters, situation)
   - Input dialogue lines (format: "Character: Line")
   - Select which line to visualize
   - Upload 2 character images and 1 background image
   - Click "Generate" (costs 1 token)
   - View generated comic scene with speech bubble

4. **View Gallery**
   - Browse all previously generated images
   - See dialogue context for each generation

## Admin Panel

Access at `/admin/` (requires superuser account)

**Manage:**
- Users and profiles
- Token packages (pricing, availability)
- Purchase records
- Generated images

## API Integration Details

### Gemini Integration
- Model: gemini-1.5-flash
- Purpose: Generate structured scene descriptions from dialogue
- Output: JSON with subject_description, setting_and_scene, action_or_expression, camera_and_style, full_image_prompt

### Qwen Integration
- Model: qwen-image-edit
- API Endpoint: https://dashscope-intl.aliyuncs.com/api/v1
- Purpose: Combine character images and background into comic panel
- Adds empty speech bubbles for dialogue

### Stripe Integration
- Checkout Sessions for payment processing
- Webhooks for payment confirmation
- Session metadata tracks user and token amount

## Security Considerations

- CSRF protection enabled on all forms
- Authentication required for all generation/purchase endpoints
- Webhook endpoint uses signature verification
- API keys stored in environment variables (Replit Secrets)
- User uploaded files stored in media directory (temporary)

## Known Limitations

1. **API Keys Required:** Full functionality requires external API keys (Gemini, Qwen, Stripe)
2. **Development Server:** Currently using Django development server (not production-ready)
3. **File Storage:** Images stored temporarily; no permanent storage for uploads
4. **Single Language:** English only

## Recent Changes (October 19, 2025)

- Initial Django project setup
- Created all three apps (accounts, tokens, generator)
- Implemented user authentication system
- Built token economy with Stripe integration
- Migrated image generation code from standalone script to Django views
- Fixed critical bug: renamed `messages` variable to `conversation_messages` to avoid shadowing Django messages framework
- Created comprehensive templates with Bootstrap 5
- Set up PostgreSQL database with migrations
- Created default token packages
- Configured Django Server workflow

## Future Enhancements

Potential features for future development:
- Batch processing for multiple dialogue lines
- Character library for reusable character images
- Download generated images
- Social sharing features
- Token package volume discounts
- Usage analytics dashboard
- Multiple language support
- Production deployment configuration

## Troubleshooting

### Server won't start
- Check that port 5000 is available
- Verify all migrations are applied: `python manage.py migrate`
- Check database connection (environment variables)

### Image generation fails
- Verify GEMINI_API_KEY is set in Replit Secrets
- Verify IMG_API_KEY is set in Replit Secrets
- Check user has sufficient token balance
- Verify uploaded images are valid formats

### Stripe payments not working
- Verify all three Stripe keys are configured
- Check webhook endpoint is accessible
- Review Stripe dashboard for payment status

### LSP Errors
- Some LSP warnings are expected for Django's dynamic model fields
- Critical errors have been resolved

## Contact & Support

For issues or questions, review the Django logs in the workflow output.
