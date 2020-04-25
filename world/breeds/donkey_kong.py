statblock = {}

donkey_kong_jab1 = {
    "key": "Jab1",
    "startup": 5,
    "totalframes": 24,
    "basedamage": 4.0,
    "shieldlag": 8,
    "invulnerability": range(5, 6)
}
donkey_kong_jab2={
    "key": "Jab2",
    "startup": 5,
    "totalframes": 34,
    "basedamage": 6.0,
    "shieldlag": 11,
    "invulnerability": range(5, 6)
}

donkey_kong_punch={
    "key": "Punch",
    "startup": 7,
    "totalframes": 34,
    "basedamage": 9.0,
    "shieldlag": 7,
    "invulnerability": range(7, 9)
}

donkey_kong_haymaker={
    "key": "Haymaker",
    "startup": 22,
    "totalframes": 54,
    "basedamage": 21,
    "shieldlag": 16,
    "invulnerability": range(22, 23)
}

donkey_kong_special={
    "key": "Special",
    "startup": 26,
    "totalframes": 62,
    "basedamage": 27,
    "shieldlag": 14,
    "invulnerability": range(26, 27)
}

donkey_kong_stun={
    "key": "Stun",
    "startup": 19,
    "totalframes": 47,
    "basedamage": 28,
    "shieldlag": 15,
    "invulnerability": range(19, 20)
}

donkey_kong_grab={
    "key": "Grab",
    "startup": 8,
    "totalframes": 38,
    "basedamage": 13.0,
    "shieldlag": -1,
    "invulnerability": []
}

donkey_kong_dodge={
    "key": "Dodge",
    "startup": 0,
    "totalframes": 26,
    "basedamage": 0.0,
    "shieldlag": -1,
    "invulnerability": range(3, 17)
}

statblock.update(
    {
        "attacks": {
            "jab1": donkey_kong_jab1,
            "jab2": donkey_kong_jab2,
            "punch": donkey_kong_punch,
            "haymaker": donkey_kong_haymaker,
            "special": donkey_kong_special,
            "stun": donkey_kong_stun,
            "grab": donkey_kong_grab,
            "dodge": donkey_kong_dodge,
        },
        "weight": 127,
        "knockback_sustained": 5000
    }
)
