#!/usr/bin/env python3
import logging
import pandas
import argparse
import pickle
import statistics
import csv
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import StackingClassifier
from sklearn.naive_bayes import GaussianNB
from utils import database_string, get_session
from models import Model, ModelCode, ModelDropCol, ModelWhereClause, County
from sqlalchemy import cast, Integer

logging.basicConfig(level=logging.DEBUG)

class Classifier(object):
    def __init__(self, in_model_code, db, y_col="party", label_col="county_fips", where_clauses=None, data_view="master_data", year_col="year", year_test=2020):
        self.db = db
        self.mc = in_model_code
        self.drop_cols = db.query(ModelDropCol).filter_by(model_code_id=self.mc.id).all()

        where = self.db.query(ModelWhereClause).filter_by(model_code=self.mc).all()
        if where:
            self.where = " where " + (" and ".join([wc.sql for wc in where]))
        else:
            self.where = ""

        self.engine_string = database_string
        self.query = f"select * from {data_view}{self.where}"
        self.df = pandas.read_sql_query(
            self.query,
            database_string
        ).drop(columns=[dc.column for dc in self.drop_cols])

        self.y = self.df[y_col].to_numpy()
        self.x = self.df.drop(columns=y_col).to_numpy()

        self.model_obj = self.db.query(Model).filter_by(model_code=self.mc).first()
        if not self.model_obj:

            rf = RandomForestClassifier(n_estimators=10, random_state=42)
            svr = make_pipeline(StandardScaler(), LinearSVC(random_state=42, dual=False, max_iter=1000))
            knn = KNeighborsClassifier(n_neighbors=3)
            nb = GaussianNB()
            classifiers = [
                ("rf", rf),
                ("svr", svr),
                ("knn", knn),
                ("nb", nb)
            ]
            self.model = StackingClassifier(estimators=classifiers, final_estimator=LogisticRegression())
            self.accuracy = None
            self.model_obj = Model(model_code=self.mc, accuracy=self.accuracy)
            self.db.add(self.model_obj)
            self.train()
            self.save()
        else:
            self.model = pickle.loads(self.model_obj.model_object)
            self.accuracy = self.model_obj.accuracy
        
    def train(self):
        x_train, x_test, y_train, y_test = train_test_split(self.x, self.y, test_size=0.33)
        self.model.fit(x_train, y_train)
        self.accuracy = self.model.score(x_test, y_test)

    def save(self):
        self.model_obj.model_object = pickle.dumps(self.model)
        self.model_obj.accuracy = self.accuracy
        self.db.commit()

    def predict(self, fips, in_file_path=None):
        """
        Currently hard coded to predict for 2020, or the latest election in which all data
        as available, but not trained on.
        """
        if "2020" in self.mc.id:
            raise IOError("Must be a non-2020 model code to predict 2020 results.")
        year = 2020
        logging.info(f"Selecting {self.mc.id} model ({self.mc.description})")
        if fips in ["ALL", "*"]:
            and_clause = ""
            logging.info("Predicting all counties...")
            all_counties = True
        else:
            and_clause = f" and county_fips = {fips}"
            all_counties = False
        max_year = self.db.execute(f"select max(year) from ({self.query})").scalar()
        search_year = max_year - 4

    
        data = pandas.read_sql_query(
            f"select * from ({self.query}) where year = '{search_year}'{and_clause}", 
            self.engine_string
        ).drop(columns=[dc.column for dc in self.drop_cols])

        fields = list(data.columns)
        county_fips_idx = None
        for i, f in enumerate(fields):
            if f == "county_fips":
                county_fips_idx = i - 1
                break

        y = data["party"].to_numpy()
        x = data.drop(columns=["party"]).to_numpy()

        predictions = self.model.predict(x)
        out_predictions = []
        fips_to_county = {}
        logging.info("Predictions:")
        i = 0

        for val in x:
            pred = predictions[i]
            county_id = str(int(val[county_fips_idx])).zfill(6)
            if county_id in fips_to_county:
                county = fips_to_county[county_id]
            else:
                county = self.db.query(County).filter_by(id=county_id).first()
                fips_to_county[county_id] = county

            logging.info(f"{county.name} ({county.id}): {pred}")
            out_predictions.append(
                {
                    "party_prediction" : pred,
                    "county_fips" : county_id,
                    "county_name" : county.name,
                    "state_fips": county.state.id,
                    "state_code" : county.state.code
                }
            )    
            i += 1

        if in_file_path:
            logging.info(f"Writing output to {in_file_path}")
            out_cols = ["party_prediction", "county_fips", "county_name", "state_fips", "state_code"]
            with open(in_file_path, "w") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=out_cols)
                writer.writeheader()
                writer.writerows(out_predictions)
        return out_predictions

    
def validate_model_code(in_code):
    session = get_session(database_string)
    upper_case = str(in_code).upper()
    result = session.query(ModelCode).filter_by(id=upper_case).first()
    session.close()

    if result:
        return result
    else:
        raise IOError("Invalid model code.")


def with_args(f):
    def with_args_(*args, **kwargs):
        ap = argparse.ArgumentParser(description="Build/train a model.")
        ap.add_argument("-m", "--model-code", required=True, type=validate_model_code, help="The type of model to run.")
        ap.add_argument("-c", "--county-fips", required=False, type=str, default=None, help="Optional: put in a county fips code to predict the vote results for.")
        ap.add_argument("-f", "--file-path", required=False, type=str, default=None, help="Optional: save result to .csv file at the given location.")
        return f(ap.parse_args(), *args, **kwargs)
    return with_args_


@with_args
def main(args):
    c = Classifier(args.model_code, get_session(database_string))
    if args.county_fips:
        c.predict(args.county_fips, args.file_path)


if __name__ == "__main__":
    main()
