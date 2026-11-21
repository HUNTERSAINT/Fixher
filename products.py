"""Catalogue data for Fix Her Hair Brand.

Edit this file to add wigs, services, prices and reviews.
Set `price` to a number (naira) and it shows on the site; leave it as None
and the site shows "Ask for price" with a WhatsApp enquiry button.
"""

BRAND = {
    "name": "Fix Her",
    "full_name": "Fix Her Hair Brand",
    "tagline": "Look Good. Feel Greater.",
    "phone_display": "+234 816 766 9495",
    "phone_tel": "+2348167669495",
    "whatsapp": "2348167669495",
    "instagram": "",   # e.g. "https://instagram.com/yourhandle"
    "tiktok": "",
    "address": "",     # e.g. "12 Example Street, Lagos"
    "hours": "Mon – Sat · 9am – 7pm",
}

PRODUCTS = [
    {
        "slug": "fringe-body-wave",
        "name": "Fringe Body Wave Wig",
        "category": "Wigs",
        "colour": "Jet Black",
        "texture": "Body wave with bangs",
        "length": "18 – 22 inches",
        "price": None,
        "image": "bangs.jpg",
        "image_sm": "bangs-sm.jpg",
        "badge": "Bestseller",
        "blurb": "Soft, bouncy body waves with a wispy fringe that frames the face beautifully. Glam without the effort.",
        "details": ["Pre-styled, ready to wear", "Soft full fringe", "Lightweight, breathable cap", "Can be restyled and revamped"],
    },
    {
        "slug": "spiral-curl-chocolate",
        "name": "Spiral Curl Wig · Chocolate Highlights",
        "category": "Wigs",
        "colour": "Dark Chocolate with honey highlights",
        "texture": "Bouncy spiral curls",
        "length": "20 – 26 inches",
        "price": None,
        "image": "curls.jpg",
        "image_sm": "curls-sm.jpg",
        "badge": "New",
        "blurb": "Glossy, defined spiral curls with a face-framing honey highlight. A true head-turner.",
        "details": ["Side-part styling", "Face-framing highlight", "Defined, long-lasting curls", "Installation available"],
    },
    {
        "slug": "auburn-spiral-curl",
        "name": "Auburn Spiral Curl Wig",
        "category": "Wigs",
        "colour": "Rich Auburn Copper",
        "texture": "Voluminous spiral curls",
        "length": "20 – 26 inches",
        "price": None,
        "image": "auburn.jpg",
        "image_sm": "auburn-sm.jpg",
        "badge": "Limited",
        "blurb": "A warm copper-auburn that glows in the sun. Full, glossy, show-stopping spirals.",
        "details": ["Warm copper tones", "Extra volume", "Lustrous finish", "Custom colour on request"],
    },
]

SERVICES = [
    {
        "slug": "wig-install",
        "name": "Wig Installs",
        "tag": "Flawless & Long-Lasting",
        "icon": "install",
        "image": "curls.jpg",
        "text": "A seamless, natural-looking install that sits flat, feels light and lasts. We prep, customise and style so your wig looks like it grows from your scalp.",
        "includes": ["Hairline customisation", "Secure, comfortable fit", "Finishing and styling", "Aftercare guidance"],
    },
    {
        "slug": "wigs",
        "name": "Premium Wigs",
        "tag": "Premium Quality",
        "icon": "wig",
        "image": "auburn.jpg",
        "text": "Hand-selected wigs in textures and colours that suit your style. Ready to wear or made to order.",
        "includes": ["Ready-to-wear units", "Custom colour & length", "Frontal and closure options", "Free styling advice"],
    },
    {
        "slug": "wig-revamp",
        "name": "Revamp Wigs",
        "tag": "Restore · Refresh · Reuse",
        "icon": "revamp",
        "image": "bangs.jpg",
        "text": "Tired wig? We wash, detangle, recondition, re-curl and restyle it until it looks brand new.",
        "includes": ["Deep wash & conditioning", "Detangling & restoration", "Re-curl / re-style", "Bleaching, plucking & colour touch-ups"],
    },
]

REVIEWS = [
    {"name": "Blessing A.", "text": "Fix Her never disappoints! My wig install was perfect and the hair quality is top-notch.", "service": "Wig Install"},
    {"name": "Chioma O.", "text": "I thought my old wig was finished. They revamped it and it looked brand new. Unreal.", "service": "Wig Revamp"},
    {"name": "Tolu M.", "text": "Neat hairline, super comfortable, and I got compliments all week. Booking again.", "service": "Wig Install"},
    {"name": "Amaka E.", "text": "Fast, professional and the curls are everything. Worth every naira.", "service": "Wigs"},
]

FAQS = [
    ("How long does a wig install take?", "Most installs take between 1 and 2 hours depending on the style, customisation and finishing you choose."),
    ("Can I bring my own wig?", "Yes. Bring your own and we will install, customise and style it, or revamp it first if it needs some love."),
    ("What does a revamp include?", "A deep wash, detangle, conditioning, re-curl or restyle, and optional plucking, bleaching knots or colour touch-ups."),
    ("How do I pay and secure my slot?", "Book online, then confirm on WhatsApp. We will let you know the deposit and payment options when we confirm your appointment."),
    ("How do I care for my wig after install?", "We give you simple aftercare steps after every service so your wig stays soft, shiny and long-lasting."),
]

TIME_SLOTS = ["09:00", "10:30", "12:00", "13:30", "15:00", "16:30", "18:00"]
