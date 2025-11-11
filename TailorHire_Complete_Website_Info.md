# TailorHire AI - Complete Website Information Document

**Last Updated:** November 10, 2025  
**Purpose:** Complete website specifications extracted from live implementation

---

## 1. BRAND IDENTITY

### 1.1 Color Palette

**Primary Colors:**
- Blue Shades:
  - `#3b82f6` (blue-500) - Used in gradients
  - `#2563eb` (blue-600) - Primary blue for text and elements
  - `#1d4ed8` (blue-700) - Hover states
  - `#60a5fa` (blue-400) - Light accents
  
- Purple Shades:
  - `#9333ea` (purple-600) - Primary purple for gradients
  - `#7e22ce` (purple-700) - Hover states
  - `#f3e8ff` (purple-100) - Light backgrounds
  - `#faf5ff` (purple-50) - Very light backgrounds

- Pink Shades:
  - `#ec4899` (pink-500) - Accent color
  - `#f472b6` (pink-400) - Gradient elements
  - `#db2777` (pink-600) - Used in hero gradient

- Additional Colors:
  - Yellow: `#facc15` (yellow-400) - Text gradients
  - Green: `#22c55e` (green-600) - Success states
  - Emerald: `#059669` (emerald-600) - Feature icons
  - Indigo: `#4f46e5` (indigo-600) - Feature icons

**Neutral Colors:**
- White: `#ffffff` - Backgrounds, text on dark
- Gray Scale:
  - `#f9fafb` (gray-50) - Light backgrounds
  - `#f3f4f6` (gray-100) - Section backgrounds
  - `#e5e7eb` (gray-200) - Borders
  - `#d1d5db` (gray-300) - Inactive borders
  - `#9ca3af` (gray-400) - Secondary text
  - `#6b7280` (gray-500) - Body text
  - `#4b5563` (gray-600) - Dark text
  - `#374151` (gray-700) - Headings
  - `#1f2937` (gray-800) - Dark backgrounds
  - `#111827` (gray-900) - Footer background

### 1.2 Typography

**Font Family:** Inter (sans-serif)

**Font Loading:**
- Web font loaded via Next.js font optimization
- Variable font with weights 100-900
- Fallback: Arial with size-adjust 107.40%

**Font Weights Used:**
- Regular (400) - Body text
- Medium (500) - Subheadings, buttons
- Semibold (600) - Section headings, emphasis
- Bold (700) - Main headlines, strong emphasis

**Responsive Typography Classes:**

1. **Heading 1 (responsive-h1):**
   - Mobile (base): 1.5rem (24px)
   - Small (640px+): 1.875rem (30px)
   - Medium (768px+): 2.25rem (36px)
   - Large (1024px+): 3rem (48px)
   - XL (1280px+): 3.75rem (60px)
   - 2XL (1536px+): 4.5rem (72px)

2. **Heading 2 (responsive-h2):**
   - Mobile: 1.25rem (20px)
   - Small: 1.5rem (24px)
   - Medium: 1.875rem (30px)
   - Large: 2.25rem (36px)
   - XL: 3rem (48px)
   - 2XL: 3.75rem (60px)

3. **Body Text (responsive-body):**
   - Mobile: 0.875rem (14px)
   - Small: 1rem (16px)
   - Medium: 1.125rem (18px)
   - Large: 1.25rem (20px)

---

## 2. UI COMPONENTS

### 2.1 Primary Button (btn-primary)

**Styling:**
- Background: Linear gradient from `#2563eb` to `#9333ea`
- Border Radius: 0.75rem (12px)
- Padding: 0.75rem 1.5rem (12px 24px)
- Font Weight: 600 (Semibold)
- Text Color: White
- Shadow: Medium shadow (0 10px 15px -3px rgba(0,0,0,0.1))
- Transition: All properties, 200ms

**Hover State:**
- Translates up: -0.125rem (-2px)
- Gradient changes: `#1d4ed8` to `#7e22ce`
- Shadow increases: Large shadow (0 20px 25px -5px rgba(0,0,0,0.1))

### 2.2 Secondary Button (btn-secondary)

**Styling:**
- Background: White `#ffffff`
- Border: 1px solid `#e5e7eb` (gray-200)
- Border Radius: 0.75rem (12px)
- Padding: 0.75rem 1.5rem (12px 24px)
- Font Weight: 600
- Text Color: `#111827` (gray-900)
- Shadow: Small shadow (0 1px 2px 0 rgba(0,0,0,0.05))
- Transition: All properties, 200ms

**Hover State:**
- Translates up: -0.125rem (-2px)
- Background changes to: `#f9fafb` (gray-50)
- Shadow increases: Medium shadow (0 4px 6px -1px rgba(0,0,0,0.1))

### 2.3 Card Component

**Styling:**
- Border Radius: 1rem (16px)
- Border: 1px solid `#f3f4f6` (gray-100)
- Background: White `#ffffff`
- Shadow: Extra large shadow (0 20px 25px -5px rgba(0,0,0,0.1))
- Overflow: Hidden

### 2.4 Text Area Field (textarea-field)

**Styling:**
- Width: 100%
- Border Radius: 0.75rem (12px)
- Border: 1px solid `#d1d5db` (gray-300)
- Padding: 0.75rem 1rem (12px 16px)
- Resize: None (vertical only)
- Transition: All properties, 200ms

**Focus State:**
- Ring: 2px solid `#3b82f6` (blue-500)
- Border color: Transparent

### 2.5 File Upload Area

**Default State:**
- Border: 2px dashed `#d1d5db` (gray-300)
- Border Radius: 0.75rem (12px)
- Padding: 2rem (32px)
- Background: Transparent
- Transition: All properties, 300ms

**Hover State:**
- Border Color: `#60a5fa` (blue-400)
- Background: `#f9fafb` (gray-50)

---

## 3. WEBSITE STRUCTURE

### 3.1 Navigation Bar

**Position:** Fixed at top
**Z-index:** 50
**Background:** Transparent (changes on scroll)
**Height:** 4rem (64px)

**Components:**
1. Logo (36x36px image) + "TailorHire AI" text
2. Desktop Navigation Links:
   - Optimizer (links to #optimizer)
   - Features (links to #features)
   - Blog (links to /blog)
   - About (dropdown menu)
     - Contact Us (links to /contact-us)
3. "Try for Free" CTA button (btn-primary)
4. Mobile hamburger menu icon (hidden on desktop)

**Text Colors:**
- Default: `white/90` (90% opacity)
- Hover: `#2563eb` (blue-600)

### 3.2 Hero Section

**ID:** #hero
**Layout:** Full viewport height (min-h-screen)
**Background:** Gradient

**Gradient Specification:**
```
Direction: Bottom-right diagonal (to-br)
From: #9333ea (purple-600)
Via: #db2777 (pink-600)
To: #2563eb (blue-600)
```

**Animated Background Elements:**
- 20 floating dots (2px × 2px)
- White with 20% opacity
- Random positions
- Animated with transform translateY
- Creates parallax effect

**Content Elements:**

1. **Badge:**
   - Text: "✨ Powered by Advanced AI Technology"
   - Background: white/20 with backdrop blur
   - Border Radius: Full (rounded-full)
   - Padding: 0.5rem 1rem

2. **Main Headline (H1):**
   - Text: "Transform Your Resume with [AI Power]"
   - "AI Power" has gradient: pink-400 → yellow-400
   - Font: responsive-h1
   - Color: White
   - Weight: Bold (700)

3. **Subheading:**
   - Text: "Get past ATS systems and land more interviews with our intelligent resume optimization technology that tailors your CV to any job description."
   - Font: responsive-body
   - Color: white/90
   - Max width: 4xl (56rem)

4. **Statistics Grid (3 columns on desktop):**
   - **Column 1:** "25K+ Resumes Optimized"
   - **Column 2:** "89% ATS Pass Rate"
   - **Column 3:** "3.2x More Interviews"
   - Number Color: `#f472b6` (pink-400)
   - Number Size: 2xl to 5xl (responsive)
   - Description Color: white/80

5. **Primary CTA Button:**
   - Text: "🚀 Start Optimizing Now"
   - Styling: white/20 background with backdrop blur
   - Border: 1px solid white/30
   - Padding: 1rem 2rem
   - Font size: 1.125rem (18px)

6. **Scroll Indicator (bottom center):**
   - Text: "Scroll to optimize"
   - Down arrow icon
   - Color: white/60
   - Animated bounce effect

### 3.3 Optimizer Section

**ID:** #optimizer
**Background:** `#f9fafb` (gray-50)
**Padding:** 5rem 0 (py-20)

**Section Header:**
- H2: "AI Resume Optimizer"
- Font: responsive-h2, Bold (700)
- Color: `#111827` (gray-900)
- Description below in gray-600

**Layout:** 2-column grid on large screens, 1-column on mobile

**Left Column (Input Area):**

1. **Resume Upload Card:**
   - Icon: Cloud upload (blue-600)
   - Heading: "Step 1: Upload Your Resume"
   - Drag & drop zone with dashed border
   - Supported formats: "PDF and DOCX files (max 10MB)"
   - Alternative: Textarea for pasting resume text
     - Height: 8rem (128px)
     - Placeholder: "Paste your resume content here..."

2. **Job Description Card:**
   - Icon: Document (purple-600)
   - Heading: "Step 2: Job Description"
   - Textarea:
     - Height: 10rem (160px)
     - Placeholder: "Paste the complete job description here..."
     - Required field

3. **Optimize Button:**
   - Full width
   - Text: "Optimize My Resume"
   - Styling: btn-primary
   - Size: Large (text-lg, py-4)
   - Disabled state: 50% opacity, not-allowed cursor

**Right Column (Results Area):**
- Card with min-height: 500px (mobile) to 600px (desktop)
- Empty state shows:
  - Document icon (gray-300)
  - Text: "Your Optimized Resume Will Appear Here"
  - Subtext: "Complete steps 1 & 2 to see the magic happen."

### 3.4 Features Section

**ID:** #features
**Background:** White `#ffffff`
**Padding:** 5rem 0 (py-20)

**Section Header:**
- H2: "Why TailorHire AI Works"
- Description about AI-powered platform

**Features Grid:**
- 1 column (mobile) → 2 columns (sm) → 3 columns (lg) → 4 columns (xl) → 5 columns (2xl)
- Gap: 1.5rem to 2rem

**6 Feature Cards:**

1. **AI-Powered Optimization**
   - Icon Background: `#f3e8ff` (purple-100)
   - Icon Color: `#9333ea` (purple-600)
   - Icon: Sparkles
   - Description: "Advanced machine learning algorithms analyze job descriptions and optimize your resume for maximum relevance and keyword matching."

2. **Lightning Fast Results**
   - Icon Background: `#fef9c3` (yellow-100)
   - Icon Color: `#ca8a04` (yellow-600)
   - Icon: Lightning bolt
   - Description: "Get your optimized resume in under 60 seconds. No manual editing or guesswork required."

3. **ATS-Friendly Format**
   - Icon Background: `#dcfce7` (green-100)
   - Icon Color: `#16a34a` (green-600)
   - Icon: Shield check
   - Description: "Ensures your resume passes through Applicant Tracking Systems with optimal formatting and structure."

4. **Match Score Analytics**
   - Icon Background: `#dbeafe` (blue-100)
   - Icon Color: `#2563eb` (blue-600)
   - Icon: Chart bars
   - Description: "Get detailed scoring on how well your optimized resume matches the job requirements with actionable insights."

5. **Real-time Processing**
   - Icon Background: `#e0e7ff` (indigo-100)
   - Icon Color: `#4f46e5` (indigo-600)
   - Icon: Clock
   - Description: "Watch your resume get optimized in real-time with progress indicators and detailed logs."

6. **Quality Guaranteed**
   - Icon Background: `#d1fae5` (emerald-100)
   - Icon Color: `#059669` (emerald-600)
   - Icon: Check circle
   - Description: "Our AI maintains your original experience while enhancing presentation and keyword optimization."

**Card Interactions:**
- Base: card styling with shadow-xl
- Hover: shadow-2xl, scale to 102%
- Icon hover: scale to 110%
- Heading hover: changes to blue-600

**Bottom CTA Card:**
- Background: Gradient from blue-50 to purple-50
- Border Radius: 1.5rem (24px)
- Padding: 2rem
- Heading: "Ready to Transform Your Resume?"
- Description about joining thousands of job seekers
- Button: "Start Your Optimization Now" (btn-primary)

### 3.5 Footer

**Background:** `#111827` (gray-900)
**Text Color:** White
**Padding:** 4rem 0 (py-16)

**Layout:** 5-column grid on large screens

**Column 1 & 2 (Company Info):**
- Logo + "TailorHire AI" text
- Description: "AI-powered resume tailoring to help you beat ATS systems and land more interviews."
- Color: `#9ca3af` (gray-400)

**Column 3 (Product):**
- Heading: "Product"
- Links:
  - Optimizer → /#optimizer
  - Features → /#features

**Column 4 (Company):**
- Heading: "Company"
- Links:
  - Blog → /blog
  - Contact Us → /contact-us

**Column 5 (Legal):**
- Heading: "Legal"
- Links:
  - Privacy Policy → /privacy-policy
  - Terms of Service → /terms-of-service

**Link Styling:**
- Default: `#9ca3af` (gray-400)
- Hover: White
- Transition: 200ms

**Bottom Bar:**
- Border top: 1px `#1f2937` (gray-800)
- Text: "© 2025 TailorHire AI. All rights reserved. Made with ❤️ for job seekers worldwide."
- Color: `#9ca3af` (gray-400)
- Font size: 0.875rem (14px)

---

## 4. CONTENT & MESSAGING

### 4.1 Main Value Proposition

**Primary:** "Transform Your Resume with AI Power"

**Supporting:** "Get past ATS systems and land more interviews with our intelligent resume optimization technology that tailors your CV to any job description."

### 4.2 Key Statistics

- **25K+** Resumes Optimized
- **89%** ATS Pass Rate
- **3.2x** More Interviews

### 4.3 Core Benefits (From Features)

1. AI-Powered Optimization
2. Lightning Fast Results (under 60 seconds)
3. ATS-Friendly Format
4. Match Score Analytics
5. Real-time Processing
6. Quality Guaranteed

### 4.4 Key Messaging Points

- "Powered by Advanced AI Technology"
- "Beat ATS systems"
- "Land more interviews"
- "Free to use"
- "Instant optimization"
- "No manual editing required"

---

## 5. SEO & META INFORMATION

### 5.1 Page Title
```
TailorHire AI | Free AI Resume Optimizer for Job Seekers
```

### 5.2 Meta Description
```
Instantly tailor your resume for any job description with TailorHire AI. Beat ATS systems, highlight your key skills, and land more interviews. Free to use.
```

### 5.3 Meta Author
```
The TailorHire AI Team
```

### 5.4 Keywords
```
ai resume builder, resume tailor, ats resume checker, cv optimizer, tailor resume to job description, free resume tool
```

### 5.5 Open Graph Tags

- **og:title:** TailorHire AI: Free AI Resume Tailoring Tool
- **og:description:** Stop getting rejected by ATS. TailorHire AI rewrites your resume to perfectly match the job you want, for free.
- **og:url:** https://www.tailoredhireresume.com/
- **og:site_name:** TailorHire AI
- **og:type:** website

### 5.6 Twitter Card

- **twitter:card:** summary_large_image
- **twitter:title:** TailorHire AI: Free AI Resume Tailoring Tool
- **twitter:description:** Stop getting rejected by ATS. TailorHire AI rewrites your resume to perfectly match the job you want, for free.

### 5.7 Schema.org Structured Data

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "TailorHire AI",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "description": "A free AI-powered resume optimizer that tailors your resume to any job description to help you beat ATS systems and land more interviews.",
  "url": "https://www.tailoredhireresume.com"
}
```

---

## 6. TECHNICAL IMPLEMENTATION

### 6.1 Frontend Framework

**Next.js 13+ (App Router)**
- Build ID: 44IctOry4-Zdy8EZWfqHf
- Static generation enabled
- App router structure

**React Components:**
- Server components for static content
- Client components for interactive elements

### 6.2 Styling Framework

**Tailwind CSS v3.4.0**
- MIT License
- Utility-first approach
- Custom configuration with extended colors
- Responsive utilities
- Custom classes: btn-primary, btn-secondary, card, textarea-field

**Custom CSS:**
- Responsive grid classes
- Responsive typography classes
- Custom animations

### 6.3 Fonts

**Primary:** Inter
- Loaded via Next.js font optimization
- Variable font (weight 100-900)
- Multiple unicode ranges for international support
- Fallback: Arial with size adjustments

### 6.4 Icons

**Heroicons** (via SVG)
- Outline style
- Stroke width: 1.5
- Used throughout the interface

### 6.5 Animations & Transitions

**Custom Keyframe Animations:**

1. **Float Animation:**
```css
@keyframes float {
  0%, 100% { transform: translateY(0) }
  50% { transform: translateY(-20px) }
}
```

2. **Glow Animation:**
```css
@keyframes glow {
  0% { box-shadow: 0 0 20px rgba(59,130,246,0.3) }
  100% { box-shadow: 0 0 30px rgba(59,130,246,0.6) }
}
```

3. **Pulse Animation:** (for skeleton loading)
```css
@keyframes pulse {
  50% { opacity: 0.5 }
}
```

**Transition Settings:**
- Default duration: 200ms
- Timing function: cubic-bezier(0.4, 0, 0.2, 1)
- Properties: all, colors, transform

### 6.6 Responsive Breakpoints

```
Mobile:    Base (< 640px)
Small:     640px (sm)
Medium:    768px (md)
Large:     1024px (lg)
X-Large:   1280px (xl)
2X-Large:  1536px (2xl)
```

### 6.7 Custom Scrollbar

**Styling:**
- Width: 8px
- Track: Rounded, gray-100 background
- Thumb: Rounded, gray-400 background
- Thumb hover: gray-500

### 6.8 Touch Targets (Mobile)

**Minimum size for touch devices:** 44px × 44px
- Applied to buttons, inputs, and interactive elements
- Media query: @media (pointer:coarse)

---

## 7. ANALYTICS & TRACKING

### 7.1 Google Analytics

**Tracking ID:** G-DJP31TZL00

**Implementation:**
```javascript
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-DJP31TZL00');
```

**What's Tracked:**
- Page views
- User interactions (clicks, scrolls)
- Button clicks
- Form submissions
- Conversion events

### 7.2 Performance Metrics

**Monitored:**
- Largest Contentful Paint (LCP)
- Interaction to Next Paint (INP)
- Cumulative Layout Shift (CLS)
- Time to First Byte (TTFB)

---

## 8. ASSETS & RESOURCES

### 8.1 Images

**Logo:**
- Path: /logo.png
- Sizes: 48×48 (1x), 96×96 (2x)
- Format: PNG
- Usage: Navigation bar, footer

**Icons:**
- Web App Manifest: 192×192, 512×512
- Path: /web-app-manifest-{size}.png
- Format: PNG

### 8.2 Manifest

**Path:** /manifest.json
**Purpose:** PWA configuration

---

## 9. PAGE ROUTES

### 9.1 Main Pages

- **Home:** /
- **Blog:** /blog
- **Contact Us:** /contact-us
- **Privacy Policy:** /privacy-policy
- **Terms of Service:** /terms-of-service

### 9.2 Section Anchors

- **Optimizer:** /#optimizer
- **Features:** /#features

---

## 10. USER INTERACTIONS

### 10.1 Resume Upload Flow

**Step 1:** Upload Resume
- Method 1: Drag and drop file
- Method 2: Click to browse
- Method 3: Paste text in textarea
- Accepted formats: PDF, DOCX
- Max size: 10MB

**Step 2:** Enter Job Description
- Paste full job description in textarea
- Required field
- Min height: 160px

**Step 3:** Click "Optimize My Resume"
- Button disabled until both inputs provided
- Processing state shows loading
- Results appear in right column

### 10.2 Navigation Interactions

**Desktop:**
- Hover over links changes color to blue-600
- About dropdown appears on hover
- Smooth scroll to sections

**Mobile:**
- Hamburger menu opens sidebar
- Touch-friendly 44px targets

### 10.3 Card Hover Effects

**Feature Cards:**
- Scale to 102%
- Shadow increases to 2xl
- Icon scales to 110%
- Heading color changes to blue-600
- Transition: 300ms

### 10.4 Button Interactions

**Primary Button:**
- Hover: Translates up 2px, gradient darkens, shadow increases
- Active: Slight scale down
- Disabled: 50% opacity, cursor not-allowed

**Secondary Button:**
- Hover: Translates up 2px, background lightens, shadow increases

---

## 11. ACCESSIBILITY FEATURES

### 11.1 Semantic HTML

- Proper heading hierarchy (H1 → H2 → H3)
- Section elements with IDs
- Nav element for navigation
- Footer element for footer
- Main element for content

### 11.2 ARIA Labels

- Hidden decorative elements: aria-hidden="true"
- SVG icons marked as decorative
- Semantic button elements

### 11.3 Keyboard Navigation

- Tab order follows visual flow
- Focus states on interactive elements
- Skip to content functionality via smooth scroll

### 11.4 Screen Reader Support

- Alt text on images
- Proper label associations
- Semantic HTML structure

---

## 12. PERFORMANCE OPTIMIZATIONS

### 12.1 Image Optimization

- Next.js Image component
- Lazy loading
- Responsive srcset
- WebP format support
- Priority loading for above-fold images

### 12.2 Font Optimization

- Font preloading
- Subset loading by unicode range
- Font-display: swap
- Variable font reduces HTTP requests

### 12.3 CSS Optimization

- Minified CSS
- Critical CSS inlined
- Unused CSS purged by Tailwind

### 12.4 JavaScript Optimization

- Code splitting
- Dynamic imports
- Async script loading
- Deferred non-critical scripts

### 12.5 Other Optimizations

- Smooth scrolling with CSS
- GPU-accelerated animations
- Efficient re-renders
- Minimal DOM manipulation

---

## 13. BROWSER SUPPORT

### 13.1 Minimum Requirements

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile Safari iOS 14+
- Chrome Mobile Android 90+

### 13.2 Polyfills

- Included for older browsers
- Path: /_next/static/chunks/polyfills-c67a75d1b6f99dc8.js

---

## 14. THEME CONFIGURATION

### 14.1 Color Mode

- Light mode only (currently)
- Theme color: `#3b82f6` (blue-500)

### 14.2 Design System

**Spacing Scale:** 0.25rem increments (4px)
**Border Radius:**
- Small: 0.375rem (6px)
- Medium: 0.5rem (8px)
- Large: 0.75rem (12px)
- XL: 1rem (16px)
- 2XL: 1.5rem (24px)
- Full: 9999px

**Shadows:**
- Small: 0 1px 2px rgba(0,0,0,0.05)
- Medium: 0 4px 6px rgba(0,0,0,0.1)
- Large: 0 10px 15px rgba(0,0,0,0.1)
- XL: 0 20px 25px rgba(0,0,0,0.1)
- 2XL: 0 25px 50px rgba(0,0,0,0.25)

---

## 15. NOTIFICATION SYSTEM

### 15.1 Toast Notifications

**Library:** React Hot Toast (indicated by _goober styles)

**Configuration:**
- Position: Top-right
- Duration: 4000ms (4 seconds)
- Default style:
  - Background: `#363636`
  - Text: White
- Success icon: Green (`#10b981`)
- Error icon: Red (`#ef4444`)

**Animations:**
- Entry: Scale and fade in
- Exit: Scale and fade out

---

## 16. ERROR HANDLING

### 16.1 404 Page

**Structure:**
- Heading: "404"
- Message: "This page could not be found."
- Styled with Next.js default error page design

### 16.2 Loading States

**Skeleton Screens:**
- Pulse animation
- Gray-200 background
- Rounded corners
- Maintains layout to prevent shift

---

## 17. FINAL NOTES

### 17.1 Development Details

- Built with Next.js 13+ App Router
- Styled with Tailwind CSS v3.4.0
- Type-safe with TypeScript (implied)
- Optimized for production deployment

### 17.2 Hosting Information

- Domain: https://www.tailoredhireresume.com
- SSL: Enabled
- CDN: Next.js automatic optimization

### 17.3 Build Information

- Build ID: 44IctOry4-Zdy8EZWfqHf
- Static generation: Enabled
- ISR: Not detected
- API routes: Not visible in HTML

---

**Document Version:** 2.0 (Complete)  
**Extracted From:** Live website HTML & CSS  
**Date:** November 10, 2025  
**Status:** ✅ Production-accurate specifications
