format:
	@pdm run blue src utils
	@pdm run isort src utils
	@pdm run autoflake --remove-all-unused-imports --remove-unused-variables --remove-duplicate-keys --expand-star-imports -ir src utils

