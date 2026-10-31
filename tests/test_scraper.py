import os

import pytest
from bs4 import BeautifulSoup

from app import scraper

# noinspection bad-argument-type
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')

def load_html_fixture(filename: str) -> str:
    """
    Read a specific offline HTML file from the cache repository.
    """
    with open(os.path.join(FIXTURES_DIR, filename), "r", encoding="utf-8") as f:
        return f.read()

scenarios = [
    (
        "10334_page.html",  # Standard modern set
        {
            "id": "10334",
            "name": "Retro Radio",
            "theme": "LEGO® Icons",
            "year": 2024,
            "age_group": "18+",
            "pieces": 906,
            "cover_url": "https://www.lego.com/cdn/product-assets/product.img.pri/10334_Prod.png"
        },
        [
            {
                "id": "6521147",
                "description": "Retro Radio (1/1)",
                "pdf_url": "https://www.lego.com/cdn/product-assets/product.bi.core.pdf/6521147.pdf",
                "cover_url": "https://www.lego.com/cdn/product-assets/product.bi.core.img/6521147.png",
                "size_mb": 72.69
            }
        ]
    ),
    (
        "71374_page.html",  # Large modern multi-booklet set
        {
            "id": "71374",
            "name": "Nintendo Entertainment System™",
            "theme": "LEGO® Super Mario™",
            "year": 2020,
            "age_group": "18+",
            "pieces": 2646,
            "cover_url": "https://www.lego.com/cdn/product-assets/product.img.pri/71374_Prod.jpg"
        },
        [
            {
                "id": "6336693",
                "description": "Nintendo Entertainment System™ (2/2)",
                "pdf_url": "https://www.lego.com/cdn/product-assets/product.bi.core.pdf/6336693.pdf",
                "cover_url": "https://www.lego.com/cdn/product-assets/product.bi.core.img/6336693.png",
                "size_mb": 50.52
            },
            {
                "id": "6337188",
                "description": "Nintendo Entertainment System™ (1/2)",
                "pdf_url": "https://www.lego.com/cdn/product-assets/product.bi.core.pdf/6337188.pdf",
                "cover_url": "https://www.lego.com/cdn/product-assets/product.bi.core.img/6337188.png",
                "size_mb": 37.48
            }
        ]
    ),
    (
        "17101_page.html",  # Complex educational kit without traditional instructions
        {
            "id": "17101",
            "name": "Creative Toolbox",
            "theme": "LEGO® BOOST",
            "year": 2017,
            "age_group": "7-12",
            "pieces": 847,
            "cover_url": "https://www.lego.com/cdn/product-assets/product.img.pri/17101_Prod.jpg"
        },
        [
            {
                "id": "17101_A_AutoBuilder",
                "description": "Creative Toolbox (1/1)",
                "pdf_url": "https://www.lego.com/cdn/product-assets/product.bi.additional.main.pdf/17101_A_AutoBuilder.pdf",
                "cover_url": "https://www.lego.com/cdn/product-assets/product.bi.additional.main.img/17101_A_AutoBuilder.png",
                "size_mb": 191.3
            },
            {
                "id": "17101_A_Frankie the Cat",
                "description": "Creative Toolbox (1/1)",
                "pdf_url": "https://www.lego.com/cdn/product-assets/product.bi.additional.main.pdf/17101_A_Frankie the Cat.pdf",
                "cover_url": "https://www.lego.com/cdn/product-assets/product.bi.additional.main.img/17101_A_Frankie the Cat.png",
                "size_mb": 168.36
            },
            {
                "id": "17101_A_Guitar4000",
                "description": "Creative Toolbox (1/1)",
                "pdf_url": "https://www.lego.com/cdn/product-assets/product.bi.additional.main.pdf/17101_A_Guitar4000.pdf",
                "cover_url": "https://www.lego.com/cdn/product-assets/product.bi.additional.main.img/17101_A_Guitar4000.png",
                "size_mb": 125.23
            },
            {
                "id": "17101_A_M.T.R. 4",
                "description": "Creative Toolbox (1/1)",
                "pdf_url": "https://www.lego.com/cdn/product-assets/product.bi.additional.main.pdf/17101_A_M.T.R. 4.pdf",
                "cover_url": "https://www.lego.com/cdn/product-assets/product.bi.additional.main.img/17101_A_M.T.R. 4.png",
                "size_mb": 150.06
            },
            {
                "id": "17101_A_Vernie the Robot",
                "description": "Creative Toolbox (1/1)",
                "pdf_url": "https://www.lego.com/cdn/product-assets/product.bi.additional.main.pdf/17101_A_Vernie the Robot.pdf",
                "cover_url": "https://www.lego.com/cdn/product-assets/product.bi.additional.main.img/17101_A_Vernie the Robot.png",
                "size_mb": 175.36
            }
        ]
    ),
    (
        "21134_page.html",  # Old-ish kit with low age group
        {
            "id": "21134",
            "name": "The Waterfall Base",
            "theme": "LEGO® MINECRAFT",
            "year": 2017,
            "age_group": "8+",
            "pieces": 729,
            "cover_url": "https://www.lego.com/cdn/product-assets/product.img.pri/21134_Prod.jpg"
        },
        [
            {
                "id": "6188685",
                "description": "The Waterfall Base (1/2)",
                "pdf_url": "https://www.lego.com/cdn/product-assets/product.bi.core.pdf/6188685.pdf",
                "cover_url": "https://www.lego.com/cdn/product-assets/product.bi.core.img/6188685.png",
                "size_mb": 5.29
            },
            {
                "id": "6188689",
                "description": "The Waterfall Base (2/2)",
                "pdf_url": "https://www.lego.com/cdn/product-assets/product.bi.core.pdf/6188689.pdf",
                "cover_url": "https://www.lego.com/cdn/product-assets/product.bi.core.img/6188689.png",
                "size_mb": 17.7
            }
        ]
    )
]

@pytest.mark.parametrize("fixture_name, expected, _", scenarios)
def test_metadata_parsing_scenarios(fixture_name, expected, _):
    """
    Test metadata parser against scenarios.
    """
    raw_html = load_html_fixture(fixture_name)
    soup = BeautifulSoup(raw_html, "html.parser")

    metadata = scraper.parse_metadata(soup)

    for key in ("id", "name", "theme", "year", "age_group", "pieces", "cover_url"):
        assert metadata[key] == expected[key]

@pytest.mark.parametrize("fixture_name, _, expected", scenarios)
def test_instructions_parsing_scenarios(fixture_name, _, expected):
    """
    Test instructions parser against scenarios.
    """
    raw_html = load_html_fixture(fixture_name)
    soup = BeautifulSoup(raw_html, "html.parser")

    instructions = scraper.parse_instructions(soup)

    assert len(expected) == len(instructions), f"Instruction count mismatch in {fixture_name}"

    for result_item, expected_item in zip(instructions, expected):
        for key in ("id", "description", "pdf_url", "cover_url", "size_mb"):
            assert result_item[key] == expected_item[key]
