"""TCN (Temporal Convolutional Network) — sklearn-compatible regressor.

Architecture: 3 TCNBlocks with channels=(32,32,32), kernel_size=3,
dilations=(1,2,4), global-average-pool → Linear(32,1).
Input reshaped to (batch, 1, n_lags) so conv1d acts over the lag dimension.
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import check_is_fitted


class _Chomp1d(nn.Module):
    def __init__(self, chomp_size: int) -> None:
        super().__init__()
        self.chomp_size = chomp_size

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x[:, :, : -self.chomp_size].contiguous()


class _TCNBlock(nn.Module):
    def __init__(self, in_ch: int, out_ch: int, kernel_size: int, dilation: int) -> None:
        super().__init__()
        pad = (kernel_size - 1) * dilation
        self.net = nn.Sequential(
            nn.Conv1d(in_ch, out_ch, kernel_size, dilation=dilation, padding=pad),
            _Chomp1d(pad),
            nn.ReLU(),
            nn.Conv1d(out_ch, out_ch, kernel_size, dilation=dilation, padding=pad),
            _Chomp1d(pad),
            nn.ReLU(),
        )
        self.residual = nn.Conv1d(in_ch, out_ch, 1) if in_ch != out_ch else None

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.net(x)
        res = x if self.residual is None else self.residual(x)
        return torch.relu(out + res)


class _SimpleTCN(nn.Module):
    def __init__(
        self,
        channels: tuple = (32, 32, 32),
        kernel_size: int = 3,
        dilations: tuple = (1, 2, 4),
    ) -> None:
        super().__init__()
        blocks = []
        in_ch = 1
        for out_ch, d in zip(channels, dilations):
            blocks.append(_TCNBlock(in_ch, out_ch, kernel_size, d))
            in_ch = out_ch
        self.tcn = nn.Sequential(*blocks)
        self.fc = nn.Linear(in_ch, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, n_lags) → (batch, 1, n_lags)
        out = self.tcn(x.unsqueeze(1))      # (batch, 32, n_lags)
        out = out.mean(dim=2)               # global avg pool → (batch, 32)
        return self.fc(out).squeeze(-1)     # (batch,)


class TCNRegressor(BaseEstimator, RegressorMixin):
    """Sklearn-compatible TCN regressor.

    All constructor args are plain Python types so sklearn clone() works.
    """

    def __init__(
        self,
        channels: tuple = (32, 32, 32),
        kernel_size: int = 3,
        dilations: tuple = (1, 2, 4),
        lr: float = 0.001,
        epochs: int = 100,
        batch_size: int = 64,
        patience: int = 10,
        random_state: int = 42,
    ) -> None:
        self.channels = channels
        self.kernel_size = kernel_size
        self.dilations = dilations
        self.lr = lr
        self.epochs = epochs
        self.batch_size = batch_size
        self.patience = patience
        self.random_state = random_state

    def fit(self, X: np.ndarray, y: np.ndarray) -> "TCNRegressor":
        torch.manual_seed(self.random_state)
        np.random.seed(self.random_state)

        X = np.asarray(X, dtype=np.float32)
        y = np.asarray(y, dtype=np.float32)
        n = len(X)

        self.x_scaler_ = StandardScaler()
        self.y_scaler_ = StandardScaler()
        Xs = self.x_scaler_.fit_transform(X).astype(np.float32)
        ys = self.y_scaler_.fit_transform(y.reshape(-1, 1)).ravel().astype(np.float32)

        val_size = max(1, int(0.1 * n))
        X_tr, X_val = Xs[:-val_size], Xs[-val_size:]
        y_tr, y_val = ys[:-val_size], ys[-val_size:]

        self.model_ = _SimpleTCN(
            channels=self.channels,
            kernel_size=self.kernel_size,
            dilations=self.dilations,
        )
        opt = torch.optim.Adam(self.model_.parameters(), lr=self.lr)
        crit = nn.MSELoss()

        Xtr_t = torch.from_numpy(X_tr)
        ytr_t = torch.from_numpy(y_tr)
        Xval_t = torch.from_numpy(X_val)
        yval_t = torch.from_numpy(y_val)

        best_val = float("inf")
        patience_left = self.patience
        best_state: dict | None = None

        for _ in range(self.epochs):
            self.model_.train()
            perm = torch.randperm(len(Xtr_t))
            for i in range(0, len(Xtr_t), self.batch_size):
                idx = perm[i : i + self.batch_size]
                opt.zero_grad()
                crit(self.model_(Xtr_t[idx]), ytr_t[idx]).backward()
                opt.step()

            self.model_.eval()
            with torch.no_grad():
                val_loss = crit(self.model_(Xval_t), yval_t).item()

            if val_loss < best_val:
                best_val = val_loss
                patience_left = self.patience
                best_state = {k: v.clone() for k, v in self.model_.state_dict().items()}
            else:
                patience_left -= 1
                if patience_left <= 0:
                    break

        if best_state is not None:
            self.model_.load_state_dict(best_state)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        check_is_fitted(self, ["model_", "x_scaler_", "y_scaler_"])
        X = np.asarray(X, dtype=np.float32)
        Xs = self.x_scaler_.transform(X).astype(np.float32)
        self.model_.eval()
        with torch.no_grad():
            preds = self.model_(torch.from_numpy(Xs)).numpy()
        return self.y_scaler_.inverse_transform(preds.reshape(-1, 1)).ravel()
