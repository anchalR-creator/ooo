
STYLE_OPTIONS = {
    "casual": {
        "tops": ["Basic T-shirt", "Relaxed-fit shirt", "Casual top"],
        "bottoms": ["Straight-fit jeans", "Chinos", "Wide-leg trousers"],
        "shoes": ["Sneakers", "Casual loafers"],
        "extras": ["Minimal watch", "Everyday bag"],
    },
    "formal": {
        "tops": ["Formal shirt", "Structured blouse", "Tailored blazer"],
        "bottoms": ["Formal trousers", "Tailored pants", "Pencil skirt"],
        "shoes": ["Formal shoes", "Block heels"],
        "extras": ["Classic watch", "Structured handbag"],
    },
    "streetwear": {
        "tops": ["Oversized graphic T-shirt", "Hoodie", "Layered shirt"],
        "bottoms": ["Cargo pants", "Baggy jeans", "Relaxed-fit trousers"],
        "shoes": ["High-top sneakers", "Chunky sneakers"],
        "extras": ["Crossbody bag", "Cap"],
    },
    "ethnic": {
        "tops": ["Kurta", "Straight-cut kurta", "Ethnic tunic"],
        "bottoms": ["Palazzo pants", "Straight pants", "Churidar"],
        "shoes": ["Juttis", "Ethnic sandals"],
        "extras": ["Traditional earrings", "Ethnic bag"],
    },
    "minimalist": {
        "tops": ["Plain fitted top", "Clean-cut shirt", "Neutral knit top"],
        "bottoms": ["Straight-leg trousers", "Classic jeans", "Tailored pants"],
        "shoes": ["White sneakers", "Minimal loafers"],
        "extras": ["Simple jewellery", "Minimal watch"],
    },
    "sporty": {
        "tops": ["Athletic T-shirt", "Sports sweatshirt", "Performance top"],
        "bottoms": ["Joggers", "Track pants", "Athletic leggings"],
        "shoes": ["Running shoes", "Training sneakers"],
        "extras": ["Sports watch", "Cap"],
    },
}

OCCASION_TIPS = {
    "college": "Choose comfortable pieces suitable for a full day on campus.",
    "office": "Keep the outfit polished and appropriate for work.",
    "party": "Use a statement piece to make the outfit stand out.",
    "date": "Balance comfort with a little personal flair.",
    "wedding": "Choose occasion-appropriate fabrics and refined accessories.",
    "travel": "Prioritise comfortable layers and practical footwear.",
    "casual": "Keep the combination relaxed and easy to wear.",
}

COLOR_PAIRS = {
    "black": "Beige",
    "white": "Navy Blue",
    "beige": "Brown",
    "brown": "Cream",
    "blue": "White",
    "navy": "White",
    "navy blue": "White",
    "red": "Black",
    "pink": "White",
    "green": "Beige",
    "olive": "Cream",
    "yellow": "Navy Blue",
    "purple": "White",
    "grey": "Black",
    "gray": "Black",
    "cream": "Brown",
    "maroon": "Beige",
    "orange": "Navy Blue",
}

SKIN_TONE_COLORS = {
    "warm": ["Olive", "Mustard", "Cream", "Rust"],
    "cool": ["Navy Blue", "Lavender", "Emerald", "Rose"],
    "neutral": ["Beige", "Teal", "Dusty Pink", "Grey"],
    "deep": ["Mustard", "Emerald", "Cream", "Burgundy"],
    "medium": ["Olive", "Teal", "Coral", "Cream"],
    "fair": ["Navy Blue", "Sage Green", "Burgundy", "Lavender"],
}


def normalise(value):
    return str(value or "").strip().lower()


def contains_any(value, keywords):
    value = normalise(value)
    return any(keyword in value for keyword in keywords)


def get_colour_pair(colour):
    return COLOR_PAIRS.get(normalise(colour), "White")


def get_fit_tip(body_type, height):
    body = normalise(body_type)

    fit_tips = {
        "hourglass": (
            "Experiment with balanced silhouettes and defined waistlines."
        ),
        "pear": (
            "Experiment with balanced upper and lower silhouettes and layering."
        ),
        "apple": (
            "Try comfortable structured layers and different trouser silhouettes."
        ),
        "rectangle": (
            "Experiment with layers, textures and different silhouettes."
        ),
        "inverted triangle": (
            "Try relaxed lower silhouettes and balanced proportions."
        ),
    }

    tip = fit_tips.get(
        body,
        "Experiment with different silhouettes and comfortable clothing."
    )

    return (
        tip + " Try different garment lengths to find proportions "
        "you personally enjoy."
    )


def classify_item(item):
    """
    Classify an existing wardrobe record using its name and category.

    Returns:
        top, bottom, one_piece, footwear, accessory, outerwear or other
    """

    name = normalise(item.name)
    category = normalise(item.category)

    # Specific clothing names take priority over broad categories.
    if contains_any(name, [
        "sneaker", "shoe", "sandals", "heels",
        "boots", "loafers", "juttis"
    ]):
        return "footwear"

    if contains_any(name, [
        "watch", "handbag", "bag", "belt", "cap",
        "hat", "earring", "necklace", "bracelet",
        "jewellery", "jewelry", "scarf"
    ]):
        return "accessory"

    if contains_any(name, [
        "lehenga", "gown", "dress", "jumpsuit",
        "romper", "indo-western", "indo western",
        "one piece", "one-piece"
    ]):
        return "one_piece"

    if contains_any(name, [
        "jacket", "coat", "cardigan", "blazer",
        "overcoat", "outerwear"
    ]):
        return "outerwear"

    if contains_any(name, [
        "jeans", "trousers", "trouser", "pants",
        "pant", "shorts", "skirt", "leggings",
        "legging", "palazzo", "churidar"
    ]):
        return "bottom"

    if contains_any(name, [
        "t-shirt", "tshirt", "tee", "tank top",
        "shirt", "blouse", "kurta", "top",
        "hoodie", "sweatshirt", "sweater", "tunic"
    ]):
        return "top"

    # Fall back to the stored category when the name is unclear.
    if category in ["tops", "top", "upper wear"]:
        return "top"

    if category in ["bottoms", "bottom", "lower wear"]:
        return "bottom"

    if category in ["dresses", "dress", "gown"]:
        return "one_piece"

    if category in ["ethnic", "fusion", "indo-western", "indo western"]:
        return "one_piece"

    if category in ["footwear", "shoes", "shoe"]:
        return "footwear"

    if category in ["accessories", "accessory"]:
        return "accessory"

    if category in ["outerwear", "jackets", "coats"]:
        return "outerwear"

    return "other"


def choose_optional_item(items, index):
    if not items:
        return None

    return items[index % len(items)]


def get_styling_tip(top_colour, bottom_colour):
    top = normalise(top_colour)
    bottom = normalise(bottom_colour)

    if top == "not specified" or bottom == "not specified":
        return "Experiment with the combination and choose what feels comfortable."

    if top == bottom:
        return (
            f"A {top_colour} monochrome combination can create a coordinated "
            "look. Try different textures to add visual interest."
        )

    return (
        f"Combine your {top_colour} top with {bottom_colour} bottoms "
        "for a coordinated look."
    )


def create_outfit_recommendations(request, wardrobe_items=None):
    style = normalise(request.style)
    occasion = normalise(request.occasion)
    mood = normalise(request.mood)
    skin_tone = normalise(request.skin_tone)

    selected_style = STYLE_OPTIONS.get(
        style, STYLE_OPTIONS["casual"]
    )

    colours = [
        colour.strip().title()
        for colour in request.preferred_colors
        if colour and colour.strip()
    ]

    if not colours:
        colours = ["Black", "White", "Beige"]

    skin_colors = SKIN_TONE_COLORS.get(
        skin_tone,
        ["Navy Blue", "Olive", "Cream", "Burgundy"]
    )

    wardrobe_items = wardrobe_items or []

    # Classify all existing wardrobe records.
    classified = {
        "top": [],
        "bottom": [],
        "one_piece": [],
        "footwear": [],
        "accessory": [],
        "outerwear": [],
        "other": [],
    }

    for item in wardrobe_items:
        item_type = classify_item(item)
        classified[item_type].append(item)

    recommendations = []
    used_pairs = set()
    used_one_piece_ids = set()

    tops = classified["top"]
    bottoms = classified["bottom"]
    dresses = classified["one_piece"]

    shoes = classified["footwear"]
    accessories = classified["accessory"]
    outerwear = classified["outerwear"]

    # 1. Recommend complete dresses and one-piece outfits first.
    for item in dresses:
        if len(recommendations) >= 3:
            break

        used_one_piece_ids.add(item.id)

        shoe = choose_optional_item(shoes, len(recommendations))
        accessory = choose_optional_item(
            accessories, len(recommendations)
        )
        layer = choose_optional_item(
            outerwear, len(recommendations)
        )

        recommendations.append({
            "outfit_number": len(recommendations) + 1,
            "title": f"{item.name} - Complete Look",
            "top": None,
            "bottom": None,
            "one_piece": {
                "item": item.name,
                "colour": item.color or "Not specified",
                "source": "wardrobe",
                "image_reference": item.image_reference,
            },
            "footwear": (
                shoe.name if shoe else
                selected_style["shoes"][
                    len(recommendations) % len(selected_style["shoes"])
                ]
            ),
            "accessories": (
                [accessory.name] if accessory else
                [selected_style["extras"][
                    len(recommendations) % len(selected_style["extras"])
                ]]
            ),
            "outerwear": layer.name if layer else None,
            "styling_tip": (
                f"Your {item.name} is a complete outfit. "
                "Add suitable footwear and accessories to finish the look."
            ),
            "source": "wardrobe one-piece",
        })

    # 2. Generate unique combinations from wardrobe tops and bottoms.
    for top in tops:
        if len(recommendations) >= 3:
            break

        for bottom in bottoms:
            if len(recommendations) >= 3:
                break

            pair = (top.id, bottom.id)

            if pair in used_pairs:
                continue

            used_pairs.add(pair)

            top_colour = top.color or "Not specified"
            bottom_colour = bottom.color or "Not specified"

            shoe = choose_optional_item(shoes, len(recommendations))
            accessory = choose_optional_item(
                accessories, len(recommendations)
            )
            layer = choose_optional_item(
                outerwear, len(recommendations)
            )

            recommendations.append({
                "outfit_number": len(recommendations) + 1,
                "title": f"{style.title()} Wardrobe Look {len(recommendations) + 1}",
                "top": {
                    "item": top.name,
                    "colour": top_colour,
                    "source": "wardrobe",
                    "image_reference": top.image_reference,
                },
                "bottom": {
                    "item": bottom.name,
                    "colour": bottom_colour,
                    "source": "wardrobe",
                    "image_reference": bottom.image_reference,
                },
                "one_piece": None,
                "footwear": (
                    shoe.name if shoe else
                    selected_style["shoes"][
                        len(recommendations) % len(selected_style["shoes"])
                    ]
                ),
                "accessories": (
                    [accessory.name] if accessory else
                    [selected_style["extras"][
                        len(recommendations) % len(selected_style["extras"])
                    ]]
                ),
                "outerwear": layer.name if layer else None,
                "styling_tip": get_styling_tip(
                    top_colour, bottom_colour
                ),
                "source": "wardrobe top + wardrobe bottom",
            })

    # 3. Fill remaining recommendations with catalogue combinations.
    catalogue_index = 0

    while len(recommendations) < 3:
        top_name = selected_style["tops"][
            catalogue_index % len(selected_style["tops"])
        ]

        bottom_name = selected_style["bottoms"][
            catalogue_index % len(selected_style["bottoms"])
        ]

        top_colour = colours[
            catalogue_index % len(colours)
        ]

        bottom_colour = get_colour_pair(top_colour)

        recommendations.append({
            "outfit_number": len(recommendations) + 1,
            "title": f"{style.title()} Catalogue Look {catalogue_index + 1}",
            "top": {
                "item": top_name,
                "colour": top_colour,
                "source": "catalogue",
                "image_reference": None,
            },
            "bottom": {
                "item": bottom_name,
                "colour": bottom_colour,
                "source": "catalogue",
                "image_reference": None,
            },
            "one_piece": None,
            "footwear": selected_style["shoes"][
                catalogue_index % len(selected_style["shoes"])
            ],
            "accessories": [
                selected_style["extras"][
                    catalogue_index % len(selected_style["extras"])
                ]
            ],
            "outerwear": None,
            "styling_tip": get_styling_tip(
                top_colour, bottom_colour
            ),
            "source": "recommendation catalogue",
        })

        catalogue_index += 1

    return {
        "recommendations": recommendations,
        "personalisation": {
            "body_type": request.body_type,
            "skin_tone": request.skin_tone,
            "height": request.height,
            "occasion": request.occasion,
            "style": request.style,
            "preferred_colors": colours,
            "mood": request.mood,
        },
        "wardrobe_summary": {
            "total_items": len(wardrobe_items),
            "tops_available": len(tops),
            "bottoms_available": len(bottoms),
            "complete_outfits_available": len(dresses),
            "footwear_available": len(shoes),
            "accessories_available": len(accessories),
            "outerwear_available": len(outerwear),
            "unclassified_items": len(classified["other"]),
        },
        "colour_guidance": {
            "additional_suggestions": skin_colors,
            "note": "These are optional colour ideas, not strict skin-tone rules.",
        },
        "fit_guidance": get_fit_tip(
            request.body_type,
            request.height
        ),
        "occasion_tip": OCCASION_TIPS.get(
            occasion,
            "Choose pieces suitable for the setting and your comfort."
        ),
        "mood_tip": (
            f"Your selected mood is {mood}."
            if mood else
            "Choose the look that reflects your personality."
        ),
        "engine": (
            "OutfitAura Wardrobe Classification and "
            "Rule-Based Recommendation Engine"
        ),
    }
