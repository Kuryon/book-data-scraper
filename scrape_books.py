import csv
import sys
from typing import List, Dict

import requests
from bs4 import BeautifulSoup


def fetch_page(url: str) -> str:
    """Fetch the HTML content of a page using requests."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as error:
        raise RuntimeError(f"Request failed for {url}: {error}") from error


def parse_books(html: str) -> List[Dict[str, str]]:
    """Parse product data from the category page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    book_cards = soup.select("article.product_pod")
    books: List[Dict[str, str]] = []

    for card in book_cards:
        title = "N/A"
        price = "N/A"
        availability = "N/A"

        try:
            title = card.find("h3").find("a")["title"].strip()
        except (AttributeError, TypeError, KeyError):
            title = "Title not found"

        try:
            price = card.select_one("p.price_color").text.strip()
        except AttributeError:
            price = "Price not found"

        try:
            availability = card.select_one("p.instock.availability").text.strip()
        except AttributeError:
            availability = "Availability not found"

        books.append({
            "title": title,
            "price": price,
            "availability": availability,
        })

    return books


def save_to_csv(books: List[Dict[str, str]], filename: str) -> None:
    """Save the scraped book data to a CSV file."""
    fieldnames = ["title", "price", "availability"]

    try:
        with open(filename, mode="w", encoding="utf-8-sig", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for book in books:
                writer.writerow(book)
    except OSError as error:
        raise RuntimeError(f"Failed to write CSV file {filename}: {error}") from error


def main() -> None:
    """Main entry point for the scraper script."""
    category_url = (
        "https://books.toscrape.com/catalogue/category/books/travel_2/index.html"
    )
    output_filename = "books_category.csv"

    if len(sys.argv) > 1:
        category_url = sys.argv[1]
    if len(sys.argv) > 2:
        output_filename = sys.argv[2]

    print(f"Scraping category page: {category_url}")

    try:
        html = fetch_page(category_url)
        books = parse_books(html)

        if not books:
            print("No book items were found on this page.")
            return

        save_to_csv(books, output_filename)
        print(f"Saved {len(books)} records to {output_filename}")
    except RuntimeError as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
