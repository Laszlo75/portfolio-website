# Mr. Laszlo Szabo - Personal Website

This repository contains the source code for Dr. Laszlo Szabo's personal website, built using [Quarto](https://quarto.org/).

## About

Mr. Laszlo Szabo is a Consultant Transplant Surgeon with a clinical and research focus on kidney and pancreas transplantation, organ retrieval, organ utilisation, and perioperative outcomes. Based at the Cardiff Transplant Unit, he leads initiatives aimed at improving access to transplantation, refining donor risk stratification, and optimising post-transplant care.

## Website Features

- **About Page**: Personal and professional information
- **Publications**: Academic publications and research contributions
- **Posts**: Blog posts and articles
- **Resume**: Professional background and experience
- **Contact Information**: Social media links and professional contacts

## Technology Stack

- **Framework**: [Quarto](https://quarto.org/) - An open-source scientific and technical publishing system
- **Language**: R/RMarkdown
- **Styling**: Custom CSS with Bootstrap
- **Icons**: FontAwesome icons for social media links

## Project Structure

```
├── _quarto.yml           # Quarto configuration file
├── _variables.yml        # Site variables
├── about.qmd            # About page content
├── index.qmd            # Homepage content
├── posts.qmd            # Blog posts listing
├── publications.qmd     # Publications page
├── resume.qmd           # Resume/CV page
├── styles.css           # Custom CSS styling
├── images/              # Image assets
│   ├── profile_pic.jpeg # Profile picture
│   └── CV short 2023-04.pdf # CV document
├── posts/               # Blog posts directory
│   └── _metadata.yml    # Posts metadata
├── _extensions/         # Quarto extensions
└── _site/              # Generated website files
```

## Local Development

### Prerequisites

- [R](https://www.r-project.org/) (version 4.0 or higher)
- [RStudio](https://www.rstudio.com/) (recommended)
- [Quarto](https://quarto.org/docs/get-started/) CLI

### Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/laszlo75/[repository-name].git
   cd [repository-name]
   ```
2. Install required R packages:

   ```r
   # Install Quarto if not already installed
   install.packages("quarto")
   ```
3. Preview the website locally:

   ```bash
   quarto preview
   ```

   or in RStudio, use the "Render" button

### Building the Site

To build the website for deployment:

```bash
quarto render
```

The generated website will be in the `_site/` directory.

## Deployment

The website can be deployed to various platforms including:

- GitHub Pages
- Netlify
- Vercel
- Quarto Pub

## Customization

### Adding New Content

- **Blog Posts**: Add new `.qmd` files in the `posts/` directory
- **Pages**: Create new `.qmd` files in the root directory and update `_quarto.yml`
- **Publications**: Update `publications.qmd` and the associated `.bib` file

### Styling

- Custom styles can be added to `styles.css`
- Site-wide variables can be modified in `_variables.yml`
- Quarto configuration can be adjusted in `_quarto.yml`

## Contact

- **Email**: [laszlo.szabo@wales.nhs.uk](mailto:laszlo.szabo@wales.nhs.uk)
- **Twitter**: [@drszabolaszlo](https://x.com/drszabolaszlo)
- **LinkedIn**: [drszabolaszlo](https://linkedin.com/in/drszabolaszlo)
- **GitHub**: [laszlo75](https://github.com/laszlo75)

## License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

---

*This website showcases the professional work and research contributions of Dr. Laszlo Szabo in the field of transplant surgery and medical research.*
