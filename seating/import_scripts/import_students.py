import pandas as pd
from seating.models import Student, Semester

def clean_column(col):
    """ Normalize column names for safety """
    return col.strip().upper().replace(" ", "").replace("_", "")

def import_students():
    file_path = "seating/import_scripts/students_data.xlsx"

    # Read ALL sheets
    all_sheets = pd.read_excel(file_path, sheet_name=None)

    total_created = 0
    total_updated = 0

    for sheet_name, df in all_sheets.items():
        print(f"\nImporting sheet: {sheet_name}")

        # Normalize all column names
        df.columns = [clean_column(col) for col in df.columns]

        created = 0
        updated = 0

        for i, row in df.iterrows():

            # Map possible name variations
            usn = row.get("USN")
            name = row.get("NAME") or row.get("STUDENTNAME") or row.get("FULLNAME")
            email = row.get("EMAIL")
            dept = row.get("DEPARTMENT")
            sem = row.get("SEMESTER")

            if pd.isna(usn) or pd.isna(name) or pd.isna(sem):
                print(f"Skipping invalid row in {sheet_name}: {row}")
                continue

            sem_number = int(sem)
            sem_obj, _ = Semester.objects.get_or_create(number=sem_number)

            obj, is_created = Student.objects.update_or_create(
                usn=usn,
                defaults={
                    "name": name,
                    "email": email,
                    "department": dept,
                    "semester": sem_obj
                }
            )

            if is_created:
                created += 1
            else:
                updated += 1

        print(f"Sheet {sheet_name}: Created {created}, Updated {updated}")
        total_created += created
        total_updated += updated

    print("\nIMPORT COMPLETED")
    print(f"Total Created: {total_created}, Total Updated: {total_updated}")
